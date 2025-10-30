from __future__ import annotations
from typing import Optional, Dict, Tuple, List
from game.rules import lock_level_for_depth, doors_match, can_place_room, deal_room_choices
from game.rng import RNG
from game.rooms import RoomType, PlacementCtx, DIRS

# 测试辅助工具
# placed: {(r,c): {"N":bool,"S":bool,"W":bool,"E":bool}}
def make_ctx(rows=5, cols=9, placed=None):
    placed = placed or {}
    def grid_doors_view(r: int, c: int) -> Optional[Dict[str, bool]]:
        return placed.get((r, c), None)
    return PlacementCtx(rows, cols, grid_doors_view)

def mk_room(name: str,
            doors: Dict[str, bool] | None = None,
            gem_cost: int = 0,
            rarity: int = 0,
            can_place=lambda pos, ctx: True) -> RoomType:
    doors = doors or {"N": False, "S": False, "W": False, "E": False}
    return RoomType(name=name, color="blue", doors=doors,
                    gem_cost=gem_cost, rarity=rarity, can_place=can_place)

#锁级分布
def test_lock_edges_are_fixed():
    rng = RNG(123)
    assert lock_level_for_depth(0, 5, rng) == 0
    assert lock_level_for_depth(4, 5, rng) == 2

def test_lock_middle_trend_increases_with_depth():
    trials = 2000
    rng1 = RNG(1)
    p2_row1 = sum(1 for _ in range(trials) if lock_level_for_depth(1, 5, rng1) == 2)

    rng3 = RNG(3)
    p2_row3 = sum(1 for _ in range(trials) if lock_level_for_depth(3, 5, rng3) == 2)

    # 越深的行（row=3）应该比浅层（row=1）更容易出现 2 级锁；留 5% 缓冲
    assert p2_row3 > p2_row1 + int(trials * 0.05)

#  门对齐与边界 
def test_doors_cannot_open_out_of_bounds_top():
    ctx = make_ctx(rows=5, cols=9)
    # 顶行 (0,4) 的房间不能有北门
    north_door = mk_room("R", {"N": True, "S": False, "W": False, "E": False})
    assert doors_match(north_door, (0, 4), ctx) is False

    no_north = mk_room("R", {"N": False, "S": False, "W": False, "E": False})
    assert doors_match(no_north, (0, 4), ctx) is True

def test_doors_cannot_open_out_of_bounds_left():
    ctx = make_ctx(rows=5, cols=9)
    # 最左列 (2,0) 的房间不能有西门
    west_door = mk_room("R", {"N": False, "S": False, "W": True, "E": False})
    assert doors_match(west_door, (2, 0), ctx) is False

    no_west = mk_room("R", {"N": False, "S": False, "W": False, "E": False})
    assert doors_match(no_west, (2, 0), ctx) is True

def test_doors_must_match_neighbor():
    # 在 (1,4) 已放置邻居，其朝北有门 -> 在 (0,4) 放的新房必须有南门
    placed = {(1, 4): {"N": True, "S": False, "W": False, "E": False}}
    ctx = make_ctx(rows=3, cols=9, placed=placed)

    bad = mk_room("bad", {"N": False, "S": False, "W": False, "E": False})
    assert doors_match(bad, (0, 4), ctx) is False  # 没有南门，不匹配

    ok = mk_room("ok", {"N": False, "S": True, "W": False, "E": False})
    assert doors_match(ok, (0, 4), ctx) is True   # 有南门，匹配

#自定义 can_place 
def test_can_place_room_respects_custom_can_place():
    # 只能边缘
    def edge_only(pos: Tuple[int,int], ctx: PlacementCtx) -> bool:
        r, c = pos
        return r == 0 or r == ctx.rows - 1 or c == 0 or c == ctx.cols - 1

    ctx = make_ctx(rows=5, cols=9)
    veranda = mk_room("veranda", can_place=edge_only)

    assert can_place_room(veranda, (0, 0), ctx) is True   # 边缘 OK
    assert can_place_room(veranda, (2, 4), ctx) is False  # 中心不行

# 三选一（最小验证）
def test_deal_room_choices_has_zero_cost_when_possible():
    # 位置选择一个不越界的位置，且周围都未放置 -> 任意门型都不受邻居约束
    ctx = make_ctx(rows=5, cols=9)

    # 构造一批“合法”的候选：全部 doors 关着，保证不会因门对齐失败
    zero1 = mk_room("zero1", gem_cost=0, rarity=0)
    zero2 = mk_room("zero2", gem_cost=0, rarity=1)
    cost1 = mk_room("c1", gem_cost=1, rarity=0)
    rare2 = mk_room("r2", gem_cost=2, rarity=2)

    all_rooms = [zero1, zero2, cost1, rare2]
    rng = RNG(123)
    picks = deal_room_choices(all_rooms, pos=(2, 4), ctx=ctx, rng=rng)

    assert 1 <= len(picks) <= 3
    # 至少一个 0 宝石选项（若目录中存在 0 宝石房）
    assert any(r.gem_cost == 0 for r in picks), f"picks={[(r.name, r.gem_cost) for r in picks]}"

    # 返回的每个房间都应当可在该 pos 合法放置
    assert all(can_place_room(r, (2, 4), ctx) for r in picks)
