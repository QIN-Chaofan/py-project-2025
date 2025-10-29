from .rng import RNG
from .rules import deal_room_choices, lock_level_for_depth
from .rooms import RoomType
from typing import Literal

Stage = Literal["EXPLORE","CHOOSING","END"]

class Engine:
    def __init__(self, rows=5, cols=9):
        self.rows, self.cols = rows, cols
        self.rng = RNG(None)
        self.stage: Stage = "EXPLORE"
        # 持有只读视图或委托到 B 的 GameState / Inventory

    def start_new(self, seed: int | None):
        self.rng = RNG(seed)
        # TODO: 初始化网格与起点，放 Entrance/目标房
        self.stage = "EXPLORE"

    def open_new_door(self, pos, direction) -> None:
        # A: 生成门锁级，若锁则交给 B 的 inventory 去扣/key-check
        row = pos[0]
        lock = lock_level_for_depth(row, self.rows, self.rng)
        # -> 让 B 的 can_open/open_door 处理资源；成功才进入 CHOOSING
        self.stage = "CHOOSING"

    def deal_room_choices(self, pos) -> list[RoomType]:
        # 从剩余牌堆中抽（你维护一个 all_rooms_remaining）
        return deal_room_choices(self.all_rooms_remaining, pos, self.ctx, self.rng)
