"""Engine Facade — 第 4–5 天：串起 A 与 B 的最小可玩流程"""

from __future__ import annotations
from typing import Literal, Tuple, List, Optional, Dict
from .rng import RNG
from .rooms import RoomType, PlacementCtx, demo_room_catalog
from .rules import deal_room_choices, lock_level_for_depth, can_place_room
from .inventory import Inventory
from .items import apply_room_entry_effects

Stage = Literal["EXPLORE", "CHOOSING", "END"]

OPP = {"N": "S", "S": "N", "W": "E", "E": "W"}


class Engine:
    def __init__(self, rows=5, cols=9):
        self.rows, self.cols = rows, cols
        self.rng = RNG(None)
        self.stage: Stage = "EXPLORE"

        # —— “地图状态”最小表示：仅持有已放置房间的门 —— #
        self.placed: Dict[Tuple[int, int], Dict[str, bool]] = {}

        # 只读视图
        def grid_doors_view(r: int, c: int) -> Optional[Dict[str, bool]]:
            return self.placed.get((r, c), None)

        self.ctx = PlacementCtx(rows, cols, grid_doors_view)
        self.all_rooms_remaining: List[RoomType] = demo_room_catalog()

        # —— 玩家与选择缓存 —— #
        self.inv = Inventory()
        self.cursor: Tuple[int, int] = (0, self.cols // 2)   # 当前所在格
        self.pending_pos: Optional[Tuple[int, int]] = None   # 正在开门要放置的目标格
        self.cached_choices: List[RoomType] = []

    # ---------------- 生命周期 ---------------- #
    def start_new(self, seed: int | None = None):
        self.rng = RNG(seed)
        self.stage = "EXPLORE"
        self.placed.clear()
        self.inv = Inventory()

        # 起点：顶行中列（向南有门，便于向下探索）
        start_pos = (0, self.cols // 2)
        self.cursor = start_pos
        self.placed[start_pos] = {"N": False, "S": True, "W": False, "E": False}

    # ---------------- 探索与开门 ---------------- #
    def handle_move(self, direction: str) -> bool:
        """尝试向某方向移动：
        - 若邻格已有房且门对接，则移动并扣 1 步
        - 若邻格未放置：进入开门流程 open_new_door -> 三选一阶段
        """
        if self.stage != "EXPLORE":
            return False

        r, c = self.cursor
        dr, dc = {"N": (-1, 0), "S": (1, 0), "W": (0, -1), "E": (0, 1)}[direction]
        nr, nc = r + dr, c + dc

        # 越界直接失败
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return False

        here = self.placed.get((r, c))
        nxt = self.placed.get((nr, nc))

        # 必须本房该方向有门
        if not here or not here.get(direction, False):
            return False

        if nxt:
            # 已有房间：门必须对接；成功则移动并扣步
            if not nxt.get(OPP[direction], False):
                return False
            if not self.inv.consume_step(1):
                self.stage = "END"
                return False
            self.cursor = (nr, nc)
            self._check_end_on_arrival()
            return True
        else:
            # 未放置：进入开门流程（产生锁级并尝试支付）
            return self.open_new_door((nr, nc), from_dir=OPP[direction])

    def open_new_door(self, pos: Tuple[int, int], from_dir: str) -> bool:
        """尝试在 pos 放新房：根据当前行生成锁级，若能支付则进入 CHOOSING，缓存三选一"""
        if self.stage != "EXPLORE":
            return False
        lock = lock_level_for_depth(pos[0], self.rows, self.rng)
        if not self.inv.can_open(lock):
            return False
        if not self.inv.open_door(lock):
            return False

        # 进入三选一阶段
        self.stage = "CHOOSING"
        self.pending_pos = pos
        self.cached_choices = deal_room_choices(self.all_rooms_remaining, pos, self.ctx, self.rng)
        return True

    def reroll_choices(self) -> bool:
        """消耗 1 骰子以重抽三选一"""
        if self.stage != "CHOOSING":
            return False
        if not self.inv.reroll_choices():
            return False
        assert self.pending_pos is not None
        self.cached_choices = deal_room_choices(self.all_rooms_remaining, self.pending_pos, self.ctx, self.rng)
        return True

    # ---------------- 选择与放置 ---------------- #
    def choose_room(self, idx: int) -> bool:
        """选择 cached_choices[idx] 放置到 pending_pos；扣宝石（房间自身 gem_cost）"""
        if self.stage != "CHOOSING" or self.pending_pos is None:
            return False
        if not (0 <= idx < len(self.cached_choices)):
            return False

        room = self.cached_choices[idx]

        # 房间费用（如果房间 gem_cost>0，需要支付；不足则失败）
        if room.gem_cost > 0:
            if self.inv.gems < room.gem_cost:
                return False
            self.inv.gems -= room.gem_cost

        # 放置合法性最终确认（并真正落地）
        if not can_place_room(room, self.pending_pos, self.ctx):
            return False

        self.placed[self.pending_pos] = dict(room.doors)

        # 从牌堆移除（简单版：移除首个同名房；如需多副本，可扩展为唯一 ID）
        for i, r in enumerate(self.all_rooms_remaining):
            if r.name == room.name and r.doors == room.doors:
                self.all_rooms_remaining.pop(i)
                break

        # 入场效果
        apply_room_entry_effects(room.name, self.inv)

        # 扣步：进入新房等同于移动 1 步
        if not self.inv.consume_step(1):
            self.stage = "END"
        else:
            self.cursor = self.pending_pos
            self.stage = "EXPLORE"
            self._check_end_on_arrival()

        # 清理 pending
        self.pending_pos = None
        self.cached_choices = []
        return True

    # ---------------- 终局判定 ---------------- #
    def _check_end_on_arrival(self) -> None:
        """最小终局：步数耗尽 或 到达最底行任意格判胜"""
        if self.inv.steps <= 0:
            self.stage = "END"
            return
        r, _ = self.cursor
        if r == self.rows - 1:
            # 到达底行：视为胜利（最小规则；可替换为“到达特定终点房”）
            self.stage = "END"

