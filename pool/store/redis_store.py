import json
import logging

from typing import Dict

import redis.asyncio as aioredis

logger = logging.getLogger('redis_store')


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
