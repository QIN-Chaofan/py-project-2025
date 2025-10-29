from dataclasses import dataclass
import random
from typing import Iterable, Sequence, TypeVar

T = TypeVar("T")

@dataclass
class RNG:
    seed: int | None = None

    def __post_init__(self):
        self._rd = random.Random(self.seed)

    def randint(self, a: int, b: int) -> int:
        return self._rd.randint(a, b)

    def random(self) -> float:
        return self._rd.random()

    def choice_weighted(self, items: Sequence[T], weights: Sequence[float]) -> T:
        # 权重可为 0，内部做 normalize
        total = sum(weights)
        assert len(items) == len(weights) and total > 0
        r = self._rd.random() * total
        c = 0.0
        for x, w in zip(items, weights):
            c += w
            if r <= c:
                return x
        return items[-1]
