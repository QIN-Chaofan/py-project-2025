from typing import List, Tuple
from .rooms import RoomType, DIRS
from .rng import RNG

LockLevel = int  # 0,1,2

def within_bounds(r:int,c:int, R:int, C:int)->bool: return 0<=r<R and 0<=c<C

def doors_match(new_room: RoomType, pos: Tuple[int,int], grid_doors_view) -> bool:
    r,c = pos
    for d,(dr,dc) in DIRS.items():
        nr, nc = r+dr, c+dc
        neighbor = grid_doors_view(nr,nc) if within_bounds(nr,nc,5,9) else None
        if neighbor is None:
            # 如果邻位未放置，允许 new_room 在该方向开门（门通向未知）
            continue
        # 邻位已放置：双向门必须匹配
        opp = {"N":"S","S":"N","W":"E","E":"W"}[d]
        if new_room.doors.get(d, False) != bool(neighbor.get(opp, False)):
            return False
    return True

def can_place_room(rt: RoomType, pos, ctx) -> bool:
    if not within_bounds(pos[0],pos[1], ctx.rows, ctx.cols): return False
    if not rt.can_place(pos, ctx): return False
    return doors_match(rt, pos, ctx.grid_doors_view)

def lock_level_for_depth(row: int, total_rows: int, rng: RNG) -> LockLevel:
    # 首行全 0，末行全 2；中间行概率随 row 单调提升（示例分布）
    if row == 0: return 0
    if row == total_rows - 1: return 2
    # 线性插值：p2 随深度增长，p0 递减
    t = row / (total_rows - 1)
    p2 = 0.15 + 0.60 * t    # 中段到后段更可能 2
    p1 = 0.70 - 0.20 * t
    p0 = max(0.0, 1.0 - p1 - p2)
    r = rng.random()
    return 2 if r < p2 else (1 if r < p2 + p1 else 0)
