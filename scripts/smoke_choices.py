from game.rng import RNG
from game.rules import deal_room_choices
from game.rooms import demo_room_catalog, PlacementCtx

rng = RNG(42)
ctx = PlacementCtx(rows=5, cols=9, grid_doors_view=lambda r,c: None)
pos = (0, 4)  # 起点上方的一个空位
choices = deal_room_choices(demo_room_catalog(), pos, ctx, rng)
print([(r.name, r.gem_cost, r.rarity) for r in choices])
