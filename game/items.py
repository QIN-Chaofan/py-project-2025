"""物品与入场效果（B 主）— 第 4–5 天最小实现
给出一个统一入口 apply_room_entry_effects(room_name, inventory)
实际项目可改为按 RoomType 的自定义 effect 回调。
"""

from __future__ import annotations
from .inventory import Inventory
from typing import Callable, Dict

# 最小示例：按房间名触发入场掉落/恢复
# 真实项目可把这个映射放到 RoomType 上（如 room.entry_effect）
ENTRY_EFFECTS: Dict[str, Callable[[Inventory], None]] = {}

def _gain_small_stash(inv: Inventory) -> None:
    inv.add_item("gem", 1)
    inv.add_item("key", 1)

def _pantry_food(inv: Inventory) -> None:
    inv.add_item("step", 3)           # 立刻恢复 3 步
    inv.add_item("food", 1)           # 额外存入一份食物（可留作他用）

def _workshop_dice(inv: Inventory) -> None:
    inv.add_item("dice", 1)

def _secret_luck(inv: Inventory) -> None:
    inv.add_item("rabbit_foot", 1)    # 永久被动：后续可用于概率修正（A 来调用）

# 注册
ENTRY_EFFECTS.update({
    "Storage": _gain_small_stash,
    "Bedroom": _pantry_food,
    "Workshop": _workshop_dice,
    "Secret_Study": _secret_luck,
})

def apply_room_entry_effects(room_name: str, inv: Inventory) -> None:
    fx = ENTRY_EFFECTS.get(room_name)
    if fx:
        fx(inv)
