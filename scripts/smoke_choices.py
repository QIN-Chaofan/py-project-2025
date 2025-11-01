from __future__ import annotations
import argparse
from collections import Counter
from typing import Optional, Dict, Tuple, List

from game.rng import RNG
from game.rules import deal_room_choices
from game.rooms import demo_room_catalog, PlacementCtx

# 可选引擎（如果你还没实现 engine.py，也能跑 direct 模式）
try:
    from game.engine import Engine
    HAS_ENGINE = True
except Exception:
    HAS_ENGINE = False


def parse_pos(s: str) -> Tuple[int, int]:
    try:
        r, c = s.split(",", 1)
        return int(r), int(c)
    except Exception:
        raise argparse.ArgumentTypeError("pos 需要形如 'row,col'，例如 2,4")


def run_direct(seed: int, rows: int, cols: int, pos: Tuple[int, int], samples: int) -> None:
    rng = RNG(seed)
    catalog = demo_room_catalog()
    ctx = PlacementCtx(rows=rows, cols=cols, grid_doors_view=lambda r, c: None)

    if samples <= 1:
        choices = deal_room_choices(catalog, pos, ctx, rng)
        print(f"[direct] pos={pos} seed={seed} rows×cols={rows}×{cols}")
        if not choices:
            print("  -> 无可放置候选（可能位置/约束太严格）")
            return
        for i, r in enumerate(choices):
            print(f"  [{i}] {r.name:16s} doors={r.doors} gem={r.gem_cost} rarity={r.rarity}")
    else:
        tally = Counter()
        for _ in range(samples):
            # 这里不断抽样 choices，然后把“出现过的房间名”计数
            ch = deal_room_choices(catalog, pos, ctx, rng)
            for r in ch:
                tally[r.name] += 1
        print(f"[direct] pos={pos} seed={seed} samples={samples}")
        for name, cnt in tally.most_common():
            print(f"  {name:16s} -> {cnt}")


def run_engine(seed: int, rows: int, cols: int, pos: Tuple[int, int], samples: int) -> None:
    if not HAS_ENGINE:
        print("[engine] 找不到 Engine（还未实现或导入失败）。请用 --mode direct 或先实现 game/engine.py。")
        return

    eng = Engine(rows=rows, cols=cols)
    eng.start_new(seed=seed)

    if samples <= 1:
        # —— 为了演示 open->choices->reroll->choose，给一点资源方便支付 —— #
        eng.inv.gems = 5
        eng.inv.dice = 1

        print(f"[engine] pos={pos} seed={seed} rows×cols={rows}×{cols} stage={eng.stage}")

        # 尝试在 pos 放新房（真实流程：玩家从当前格朝某方向走到 pos，这里直接演示）
        ok = eng.open_new_door(pos, from_dir="N")  # from_dir 是“新房相对入口”的对向（示例给 N 即可）
        if not ok or eng.stage != "CHOOSING":
            print("  -> 无法进入三选一（可能资源不足或位置不合法）")
            return

        print("  初始候选：", [r.name for r in eng.cached_choices])

        # 演示重掷（如果有骰子）
        if eng.reroll_choices():
            print("  重掷后候选：", [r.name for r in eng.cached_choices])
        else:
            print("  无法重掷（没有骰子）")

        # 选择第 0 个候选并放置
        if eng.cached_choices:
            placed = eng.cached_choices[0].name
            ok = eng.choose_room(0)
            print(f"  选择并放置 -> {placed} / success={ok}")
            print("  当前位置:", eng.cursor, "剩余步数:", eng.inv.steps, "阶段:", eng.stage)
        else:
            print("  -> 没有可选择的候选项")
    else:
        # 多次抽样统计（保持你原来的统计逻辑）
        tally = Counter()
        for _ in range(samples):
            ch = eng.deal_room_choices(pos)
            for r in ch:
                tally[r.name] += 1
        print(f"[engine] pos={pos} seed={seed} samples={samples}")
        for name, cnt in tally.most_common():
            print(f"  {name:16s} -> {cnt}")
            
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["engine", "direct"], default="engine",
                    help="engine=通过 Engine Facade; direct=直接调用 deal_room_choices")
    ap.add_argument("--seed", type=int, default=42, help="随机种子（可复现）")
    ap.add_argument("--rows", type=int, default=5, help="网格行数")
    ap.add_argument("--cols", type=int, default=9, help="网格列数")
    ap.add_argument("--pos", type=parse_pos, default=(2, 4), help="放置坐标 'row,col'")
    ap.add_argument("--samples", type=int, default=1, help="抽样次数 (>1 时做频次统计)")
    args = ap.parse_args()

    if args.mode == "direct":
        run_direct(args.seed, args.rows, args.cols, args.pos, args.samples)
    else:
        run_engine(args.seed, args.rows, args.cols, args.pos, args.samples)


if __name__ == "__main__":
    main()
