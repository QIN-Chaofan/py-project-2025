from typing import List, Tuple
from .rooms import RoomType, DIRS
from .rng import RNG
from typing import Iterable
from .rooms import rarity_weight

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
def deal_room_choices(all_rooms: Iterable[RoomType],
                      pos, ctx, rng: RNG) -> list[RoomType]:
    legal = [rt for rt in all_rooms if can_place_room(rt, pos, ctx)]
    if not legal:
        return []  # 交给 engine 决定“死路”处理
    weights = [rarity_weight(rt.rarity) for rt in legal]
    picks: list[RoomType] = []
    pool = legal.copy()

    # 先尽量抽出至少 1 个 gem_cost==0
    zeros = [rt for rt in pool if rt.gem_cost == 0]
    if zeros:
        picks.append(rng.choice_weighted(zeros, [rarity_weight(r.rarity) for r in zeros]))
        pool.remove(picks[-1])

    # 抽满 3 个
    while len(picks) < 3 and pool:
        w = [rarity_weight(r.rarity) for r in pool]
        sel = rng.choice_weighted(pool, w)
        picks.append(sel)
        pool.remove(sel)

    # 若不足 3，返回已有（engine 层可提示“可再掷骰子”）
    return picks

