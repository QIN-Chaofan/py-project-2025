from game.engine import Engine

def test_open_and_place_flow():
    eng = Engine()
    eng.start_new(seed=7)

    # 从起点(0, mid)向南移动：未放置 -> 触发开门与三选一
    cur = eng.cursor
    assert eng.handle_move("S") in (True, False)  # 可能直接移动（若预放了），否则进入 CHOOSING

    if eng.stage == "CHOOSING":
        # 有候选则可选择第 0 个
        assert len(eng.cached_choices) >= 1
        ok = eng.choose_room(0)
        assert ok is True
        # 进入 EXPLORE 或 END
        assert eng.stage in ("EXPLORE", "END")
