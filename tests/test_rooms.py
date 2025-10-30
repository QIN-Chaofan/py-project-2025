from game.rooms import rarity_weight, demo_room_catalog, PlacementCtx

def test_rarity_weight_values():
    assert abs(rarity_weight(0) - 1.0) < 1e-9
    assert 0.32 < rarity_weight(1) < 0.34
    assert 0.10 < rarity_weight(2) < 0.12
    assert 0.03 < rarity_weight(3) < 0.04

def test_demo_catalog_has_zero_cost():
    cats = demo_room_catalog()
    assert any(r.gem_cost == 0 for r in cats)
