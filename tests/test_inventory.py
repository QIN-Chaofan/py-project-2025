from game.inventory import Inventory

def test_open_door_rules():
    inv = Inventory(steps=5, gems=2, keys=1, dice=0, consumables={"lockpick":1, "food":0})
    assert inv.can_open(0) and inv.open_door(0)
    # lock1 优先用 key
    assert inv.can_open(1) and inv.open_door(1)
    assert inv.keys == 0
    # 再次开 lock1，用 lockpick
    assert inv.can_open(1) and inv.open_door(1)
    assert inv.consumables["lockpick"] == 0
    # lock2 用 2 宝石
    assert inv.can_open(2) and inv.open_door(2)
    assert inv.gems == 0

def test_reroll_consumes_dice():
    inv = Inventory(dice=1)
    assert inv.reroll_choices() is True
    assert inv.dice == 0
    assert inv.reroll_choices() is False
