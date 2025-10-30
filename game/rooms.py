from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Tuple, Optional, List

Pos = Tuple[int, int]  # (row, col)

# 方向单位向量
DIRS: Dict[str, Tuple[int, int]] = {"N": (-1, 0), "S": (1, 0), "W": (0, -1), "E": (0, 1)}


class PlacementCtx:
    """
    放置上下文（由 engine/state 提供只读视图）
    rows, cols: 网格大小
    grid_doors_view(r,c) -> Optional[Dict[str,bool]]：若未放置返回 None；已放置返回该房间四向门布尔字典
    """
    def __init__(self, rows: int, cols: int, grid_doors_view):
        self.rows = rows
        self.cols = cols
        self.grid_doors_view = grid_doors_view


@dataclass(frozen=True)
class RoomType:
    name: str
    color: str                      # "blue","green","orange","purple","yellow","red" 等
    doors: Dict[str, bool]          # {"N":True, "S":False, "W":True, "E":False}
    gem_cost: int                   # 进入/放置所需宝石（0/1/2…）
    rarity: int                     # 稀有度 0..3 （越大越稀有）
    can_place: Callable[[Pos, PlacementCtx], bool]  # 额外位置限制


def rarity_weight(rarity: int, base: float = 1.0) -> float:
    """稀有度权重：每升一级，概率约 /3（0:1.0, 1:~0.333, 2:~0.111, 3:~0.037）"""
    return base / (3 ** max(0, rarity))


# 常用 can_place 规则

def can_place_any(pos: Pos, ctx: PlacementCtx) -> bool:
    return True

def can_place_edge(pos: Pos, ctx: PlacementCtx) -> bool:
    r, c = pos
    return r == 0 or r == ctx.rows - 1 or c == 0 or c == ctx.cols - 1

def can_place_inner(pos: Pos, ctx: PlacementCtx) -> bool:
    r, c = pos
    return 0 < r < ctx.rows - 1 and 0 < c < ctx.cols - 1


#  demo 房间目录（8~12 个基础房间，涵盖多门型 + 边缘限定 + 0 宝石保障）

def demo_room_catalog() -> List[RoomType]:
    R: List[RoomType] = []

    # 基础 0 宝石房：保证三选一里能抽到至少一个不花宝石
    R.append(RoomType("Bedroom", "blue",
                      {"N": False, "S": True, "W": False, "E": True},
                      gem_cost=0, rarity=0, can_place=can_place_any))
    R.append(RoomType("Hallway_NS", "green",
                      {"N": True, "S": True, "W": False, "E": False},
                      gem_cost=0, rarity=0, can_place=can_place_any))
    R.append(RoomType("Hallway_EW", "green",
                      {"N": False, "S": False, "W": True, "E": True},
                      gem_cost=0, rarity=0, can_place=can_place_any))

    # 边缘限定（例如阳台/花园/走廊外沿）
    R.append(RoomType("Veranda_NE", "yellow",
                      {"N": False, "S": True, "W": False, "E": True},
                      gem_cost=0, rarity=1, can_place=can_place_edge))
    R.append(RoomType("Garden", "yellow",
                      {"N": False, "S": True, "W": True, "E": False},
                      gem_cost=0, rarity=1, can_place=can_place_edge))

    # 拐角/三通/十字（提高联通性）
    R.append(RoomType("Corner_NE", "orange",
                      {"N": True, "S": False, "W": False, "E": True},
                      gem_cost=1, rarity=0, can_place=can_place_any))
    R.append(RoomType("T_North", "orange",
                      {"N": True, "S": False, "W": True, "E": True},
                      gem_cost=1, rarity=1, can_place=can_place_any))
    R.append(RoomType("Cross", "purple",
                      {"N": True, "S": True, "W": True, "E": True},
                      gem_cost=1, rarity=1, can_place=can_place_inner))

    # 稀有与代价更高的房（示例：金库/宝库）
    R.append(RoomType("Treasury", "red",
                      {"N": True, "S": False, "W": True, "E": False},
                      gem_cost=2, rarity=2, can_place=can_place_inner))
    R.append(RoomType("Secret_Study", "red",
                      {"N": True, "S": True, "W": False, "E": False},
                      gem_cost=2, rarity=2, can_place=can_place_inner))

    # 补充一个简单房（低代价，便于中期过渡）
    R.append(RoomType("Storage", "blue",
                      {"N": False, "S": True, "W": True, "E": False},
                      gem_cost=0, rarity=0, can_place=can_place_any))

    return R
