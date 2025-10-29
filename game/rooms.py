from dataclasses import dataclass
from typing import Callable, Tuple, Dict

Pos = Tuple[int, int]  # (row, col)
DIRS = {"N": (-1,0), "S": (1,0), "W": (0,-1), "E": (0,1)}

@dataclass(frozen=True)
class RoomType:
    name: str
    color: str              # "blue"/"green"/"orange"/"purple"/"yellow"/"red"
    doors: Dict[str, bool]  # {"N":True,"S":False,...}
    gem_cost: int           # 0/1/2/3...
    rarity: int             # 0..3
    can_place: Callable[[Pos, "PlacementCtx"], bool]

class PlacementCtx:
    def __init__(self, rows: int, cols: int, grid_doors_view):
        self.rows = rows; self.cols = cols; self.grid_doors_view = grid_doors_view
    # grid_doors_view(r,c)-> dict方向到bool，未放置返回None

def rarity_weight(rarity: int, base: float = 1.0) -> float:
    return base / (3 ** rarity)
