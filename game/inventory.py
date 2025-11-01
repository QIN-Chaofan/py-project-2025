"""背包逻辑（B 主）— 第 4–5 天最小实现
支持：步数、宝石(gems)、钥匙(keys)、骰子(dice)、被动(perks)
开门规则（示例，可按你们规则库微调）：
- lock 0：免费
- lock 1：优先消耗 key；若 key==0 且有 lockpick（一次性道具），则消耗 lockpick
- lock 2：消耗 2 宝石（不足则失败）
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Inventory:
    steps: int = 20
    gems: int = 0
    keys: int = 0
    dice: int = 0
    # 一次性道具计数
    consumables: Dict[str, int] = field(default_factory=lambda: {"lockpick": 0, "food": 0})
    # 被动（永久）效果
    perks: Dict[str, bool] = field(default_factory=lambda: {"rabbit_foot": False, "metal_detector": False})

    # ---- 通用修改 ----
    def add_item(self, name: str, qty: int = 1) -> None:
        if name == "gem":
            self.gems += qty
        elif name == "key":
            self.keys += qty
        elif name == "dice":
            self.dice += qty
        elif name in self.consumables:
            self.consumables[name] = self.consumables.get(name, 0) + qty
        elif name in self.perks:
            self.perks[name] = True
        elif name == "step":
            self.steps += qty
        else:
            # 未知道具类型：忽略或抛异常均可，这里选择忽略以稳健
            pass

    # ---- 移动与体力 ----
    def consume_step(self, n: int = 1) -> bool:
        if self.steps >= n:
            self.steps -= n
            return True
        return False

    # ---- 门锁规则 ----
    def can_open(self, lock_level: int) -> bool:
        if lock_level == 0:
            return True
        if lock_level == 1:
            return self.keys > 0 or self.consumables.get("lockpick", 0) > 0
        if lock_level == 2:
            return self.gems >= 2
        return False

    def open_door(self, lock_level: int) -> bool:
        if lock_level == 0:
            return True
        if lock_level == 1:
            if self.keys > 0:
                self.keys -= 1
                return True
            if self.consumables.get("lockpick", 0) > 0:
                self.consumables["lockpick"] -= 1
                return True
            return False
        if lock_level == 2:
            if self.gems >= 2:
                self.gems -= 2
                return True
            return False
        return False

    # ---- 重掷（三选一重抽）----
    def reroll_choices(self) -> bool:
        """消耗 1 颗骰子来重抽三选一；失败则不扣。"""
        if self.dice > 0:
            self.dice -= 1
            return True
        return False
