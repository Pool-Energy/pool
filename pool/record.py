from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from chia_rs import G1Element

from chia.pools.pool_wallet_info import PoolState
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_spend import CoinSpend
from chia.util.ints import uint64
from chia.util.streamable import streamable, Streamable


@streamable
@dataclass(frozen=True)
class FarmerRecord(Streamable):
    launcher_id: bytes32
    p2_singleton_puzzle_hash: bytes32
    delay_time: uint64
    delay_puzzle_hash: bytes32
    authentication_public_key: G1Element
    singleton_tip: CoinSpend
    singleton_tip_state: PoolState
    points: uint64
    difficulty: uint64
    payout_instructions: str
    is_pool_member: bool
    left_at: Optional[str]
    left_last_at: Optional[str]
    email: Optional[str]
    estimated_size: uint64
    last_block_timestamp: Optional[uint64]
    last_block_etw: Optional[uint64]
    name: Optional[str]
    fcm_token: Optional[str]
    push_missing_partials_hours: Optional[uint64]
    push_block_farmed: Optional[bool]
    custom_difficulty: Optional[str]
    minimum_payout: Optional[uint64]

    @property
    def left_at_datetime(self):
        if self.left_at:
            return datetime.fromisoformat(self.left_at)

    @property
    def left_last_at_datetime(self):
        if self.left_last_at:
            return datetime.fromisoformat(self.left_last_at)
