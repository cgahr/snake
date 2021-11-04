import pytest

from snake.ai_cycle import Cycle, HamiltonianCycle
from snake.dtypes import Direction
from snake.exceptions import InvalidCycleError
from snake.game import Field


class Test:
    def test1(self):
        _ = Cycle((Field(1, 1), Field(1, 2)), (Direction.UP, Direction.DOWN))

    def test2(self):
        with pytest.raises(InvalidCycleError):
            _ = Cycle((Field(1, 1),), (Direction.UP,))

    def test3(self):
        cyc1 = Cycle(
            (Field(1, 1), Field(1, 2), Field(2, 2), Field(2, 1)),
            (Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT),
        )
        cyc2 = Cycle(
            (Field(2, 1), Field(2, 2), Field(3, 2), Field(3, 1)),
            (Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT),
        )

        _ = cyc1 + cyc2

    def test4(self):
        cyc1 = Cycle(
            (Field(1, 1), Field(1, 2), Field(2, 2), Field(2, 1)),
            (Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT),
        )
        cyc2 = Cycle(
            (Field(3, 1), Field(3, 2), Field(4, 2), Field(4, 1)),
            (Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT),
        )
        return cyc1 + cyc2


class TestHamiltonianCycle:
    def test(self):
        _ = HamiltonianCycle(20, 20)
