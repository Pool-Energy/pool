import json
import logging

from typing import Dict

import redis.asyncio as aioredis

logger = logging.getLogger('redis_store')

# Redis hash used to keep track of partials currently "to be validated"
# (accepted phase-1, awaiting phase-2 confirmation). This is a regular,
# persistent key (unlike pub/sub channels, which are fire-and-forget), so a
# freshly-connected WebSocket client can fetch a snapshot of what's
# currently in progress instead of starting blank (see `api/src/api/consumers.py`).
PENDING_PARTIALS_KEY = 'partials:pending_state'


class RedisStore(object):
    """
    Thin wrapper around a Redis pub/sub connection, used to broadcast live
    events (new partials, blocks, payouts, pool status) to the `api` process
    (Django Channels), which relays them to connected WebSocket clients.

    Publishing is always best-effort: a failure here must never impact the
    critical path (accepting partials, recording blocks/payouts).
    """

    def __init__(self, pool_config: Dict):
        self.pool_config = pool_config
        redis_config = self.pool_config.get('redis') or {}
        self.host = redis_config.get('host', 'localhost')
        self.port = redis_config.get('port', 6379)
        self.client: aioredis.Redis | None = None

    async def connect(self):
        self.client = aioredis.Redis(
            host=self.host,
            port=self.port,
            socket_connect_timeout=2,
            socket_timeout=2,
        )

    async def close(self):
        if self.client is not None:
            await self.client.aclose()

    async def _publish(self, channel: str, payload: Dict) -> None:
        if self.client is None:
            return
        try:
            await self.client.publish(channel, json.dumps(payload, default=str))
        except Exception:
            logger.warning('Failed to publish live event on channel %r', channel, exc_info=True)

    async def publish_partial(self, launcher_id: str, payload: Dict) -> None:
        await self._publish('live:partial:all', payload)
        await self._publish(f'live:partial:{launcher_id}', payload)

    async def set_partial_pending(self, partial_key: str, payload: Dict) -> None:
        """Records a partial as currently "to be validated" so it can be
        included in the snapshot sent to newly-connected clients."""
        if self.client is None:
            return
        try:
            await self.client.hset(PENDING_PARTIALS_KEY, partial_key, json.dumps(payload, default=str))
        except Exception:
            logger.warning('Failed to record pending partial %r', partial_key, exc_info=True)

    async def clear_partial_pending(self, partial_key: str) -> None:
        """Removes a partial from the "to be validated" snapshot state, once
        it has been resolved (valid/stale/duplicate/invalid) or immediately
        rejected without ever going through the pending phase (no-op)."""
        if self.client is None:
            return
        try:
            await self.client.hdel(PENDING_PARTIALS_KEY, partial_key)
        except Exception:
            logger.warning('Failed to clear pending partial %r', partial_key, exc_info=True)

    async def get_all_pending_partials(self) -> Dict[str, Dict]:
        """Returns every currently-recorded "to be validated" partial
        (partial_key -> payload), used by the stuck-partials watchdog to
        detect and force-resolve entries that were orphaned by a non-graceful
        `pool` shutdown/crash (see `Pool.stuck_partials_watchdog_loop`)."""
        if self.client is None:
            return {}
        try:
            raw = await self.client.hgetall(PENDING_PARTIALS_KEY)
        except Exception:
            logger.warning('Failed to fetch pending partials', exc_info=True)
            return {}
        result = {}
        for key, value in raw.items():
            try:
                key = key.decode() if isinstance(key, bytes) else key
                value = value.decode() if isinstance(value, bytes) else value
                result[key] = json.loads(value)
            except ValueError:
                continue
        return result

    async def publish_block(self, launcher_id: str | None, payload: Dict) -> None:
        await self._publish('live:block:all', payload)
        if launcher_id:
            await self._publish(f'live:block:{launcher_id}', payload)

    async def publish_payout(self, global_payload: Dict, per_launcher: Dict[str, Dict]) -> None:
        await self._publish('live:payout:all', global_payload)
        for launcher_id, payload in per_launcher.items():
            await self._publish(f'live:payout:{launcher_id}', payload)

    async def publish_pool_status(self, payload: Dict) -> None:
        await self._publish('live:pool_status', payload)
