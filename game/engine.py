"""Engine Facade (A+B 共管) — 第三天最小可运行版（仅用于三选一演示）"""

from __future__ import annotations
from typing import Literal, Tuple, List, Optional, Dict
from .rng import RNG
from .rooms import RoomType, PlacementCtx, demo_room_catalog
from .rules import deal_room_choices, lock_level_for_depth

Stage = Literal["EXPLORE", "CHOOSING", "END"]


class Engine:
    def __init__(self, rows=5, cols=9):
        self.rows, self.cols = rows, cols
        self.rng = RNG(None)
        self.stage: Stage = "EXPLORE"

        # 简化的“已放置房间门视图”：仅用于 A 的放置校验/门对齐#
        # placed[(r,c)] = {"N":bool,"S":bool,"W":bool,"E":bool}
        self.placed: Dict[Tuple[int, int], Dict[str, bool]] = {}

        # 只读视图
        def grid_doors_view(r: int, c: int) -> Optional[Dict[str, bool]]:
            return self.placed.get((r, c), None)

        self.ctx = PlacementCtx(rows, cols, grid_doors_view)
        self.all_rooms_remaining: List[RoomType] = demo_room_catalog()

    def start_new(self, seed: int | None = None):
        self.rng = RNG(seed)
        self.stage = "EXPLORE"
        self.placed.clear()

        # 放一个起点（示例：顶行中间，向南开门以便后续衔接）
        start_pos = (0, self.cols // 2)
        self.placed[start_pos] = {"N": False, "S": True, "W": False, "E": False}

    def open_new_door(self, pos: Tuple[int, int], direction: str):
        # 最小示例：仅计算锁级，真实扣资源交给 B
        row = pos[0]
        _lock = lock_level_for_depth(row, self.rows, self.rng)
        self.stage = "CHOOSING"

    def deal_room_choices(self, pos: Tuple[int, int]) -> List[RoomType]:
        return deal_room_choices(self.all_rooms_remaining, pos, self.ctx, self.rng)

    # 仅用于示例：把选中的房间“放到网格上”
    def place_room(self, pos: Tuple[int, int], room: RoomType):
        self.placed[pos] = dict(room.doors)  # 深拷贝避免共享

