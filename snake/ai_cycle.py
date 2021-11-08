from collections import deque
from itertools import product
from typing import Optional

import numpy as np
import pygame as pg

from .ai import BaseAI
from .config import FIELD_PX
from .dtypes import Color, Content
from .exceptions import (
    CycleError,
    InvalidCycleError,
    NonAdjacentCyclesError,
    StopSearch,
)
from .game import Board, Direction, Field, Snake


def _admissible_directions(field: Field) -> set[Direction]:
    return {
        Direction.UP if field.col % 2 == 0 else Direction.DOWN,
        Direction.LEFT if field.row % 2 == 0 else Direction.RIGHT,
    }


class Cycle(dict[Field, Direction]):
    def __init__(self, fields: list[Field], directions: list[Direction]):
        super().__init__(
            {field: direction for field, direction in zip(fields, directions)}
        )
        self.is_valid_or_raise()

    def join(self, other, *, at: Field):
        pass

    def __add__(self, other):
        if set(other).issubset(self):
            return self

        intersect = set(self) & set(other)
        if len(intersect) != 0:
            for field in intersect:
                if self[field] == other[field]:
                    continue
                if field + other[field] in self:
                    continue

                while True:
                    self[field] = other[field]
                    field += self[field]

                    if field in self:
                        break
            self.is_valid_or_raise()
            return self

        neighbors = {field + d for field in set(other) for d in Direction}

        intersect = neighbors & set(self)

        if len(intersect) == 0:
            raise NonAdjacentCyclesError

        for field in intersect:
            if field + self[field] in intersect:
                break

        for direction in Direction:
            if field + direction in other:
                break

        goal = field + self[field]
        self[field] = direction
        field += self[field]

        while True:
            self[field] = other[field]
            field += self[field]

            if goal.dist(field) == 1:
                break

        for direction in Direction:
            if field + direction == goal:
                break
        self[field] = direction

        return self + other

    def dist(self, start: Field, end: Field) -> float:
        self.is_valid_or_raise()

        if start == end:
            return 0
        cur = start
        dist = 0
        while cur != end:
            cur += self[cur]
            dist += 1

            if cur == end:
                return dist
            if cur == start:
                return np.nan
        raise ValueError("idk how you get here, this should not happen")

    def is_valid_or_raise(self):
        # copy = self.__data.copy()
        copy = self.copy()

        for field in self:
            if not isinstance(field, Field):
                raise InvalidCycleError(f"{field} is not a 'Field'.")
            if not isinstance(self[field], Direction):
                raise InvalidCycleError(
                    f"value {self[field]} for field {field} is not a 'Direction'."
                )
            if field + self[field] not in self:
                raise InvalidCycleError(
                    f"{field} points to {field + self[field]} which does not exist."
                )
            try:
                copy.pop(field + self[field])
            except KeyError:
                raise InvalidCycleError(
                    f"several fields point to {field + self[field]}"
                )

        start = list(self)[0]
        cur = start + self[start]
        count = 1

        while cur != start:
            cur += self[cur]
            count += 1

        if count != len(self):
            raise InvalidCycleError(
                f"it is not possible to reach all fields starting from {start}."
            )

    def draw(self, surface: pg.Surface):
        for field, direction in self.items():
            x1, y1 = field.rect.center
            x2, y2 = (field + direction).rect.center

            size = FIELD_PX // 3
            size = size if (size % 2 == 0) else size + 1

            left = min(x1, x2) - size // 2
            top = min(y1, y2) - size // 2
            width = abs(x1 - x2) + size
            height = abs(y1 - y2) + size

            rect = pg.Rect(left, top, width, height)
            surface.fill(Color.LIGHTYELLOW.value, rect)


class HamiltonianCycle(Cycle):
    def __init__(self, cols: int, rows: int):
        directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        cycle = Cycle(
            self._fields_from_start_with_directions(Field(0, 0), directions),
            directions,
        )

        for col, row in product(range(cols), range(rows)):
            if (col % 2 == 0) and (row % 2 == 0):
                new_cycle = Cycle(
                    self._fields_from_start_with_directions(
                        Field(col, row), directions
                    ),
                    directions,
                )
                cycle = cycle + new_cycle

        super().__init__(list(cycle.keys()), list(cycle.values()))

    @classmethod
    def from_cycle(cls, cycle: Cycle):
        cycle.__class__ = HamiltonianCycle
        return cycle

    def _fields_from_start_with_directions(
        self, field: Field, directions: list[Direction]
    ) -> list[Field]:
        fields = [field]

        for direction in directions:
            fields.append(fields[-1] + direction)
        return list(fields)

    def split(self, field: Field) -> tuple[Cycle, Cycle]:
        directions = _admissible_directions(field)

        if len(directions) == 1:
            raise CycleError(f"cannot split cycles at {field}")

        direction = (directions - {self[field]}).pop()

        _field = field
        _fields = [_field]
        _directions = [direction]

        _field += direction
        while _field != field:
            _fields.append(_field)
            _directions.append(self[_field])
            _field += self[_field]

        cycle1 = Cycle(_fields, _directions)

        _fields = []
        _directions = []

        _field = field + self[field]
        while _field + self[_field] not in cycle1:
            _fields.append(_field)
            _directions.append(self[_field])
            _field += self[_field]

        _fields.append(_field)
        _directions.append((_admissible_directions(_field) - {self[_field]}).pop())

        cycle2 = Cycle(_fields, _directions)

        assert set(cycle1.keys()) & set(cycle2.keys()) == set()

        cycle1.is_valid_or_raise()
        cycle2.is_valid_or_raise()
        return cycle1, cycle2


def join_adjoint_cycles(
    cycle1: Cycle,
    cycle2: Cycle,
    start: Field,
    invalid_fields: Optional[list[Field]] = None,
):
    if set(cycle1) & set(cycle2) != set():
        raise ValueError("'cycle1' and 'cycle2' must be adjoint.")

    if start in cycle1:
        left = cycle1
        right = cycle2
    elif start in cycle2:
        left = cycle2
        right = cycle1
    else:
        raise ValueError(f"{start} is neither cycle1 not cycle2.")

    invalid_fields = [] if invalid_fields is None else invalid_fields

    field = start
    fields = set(right)
    while True:
        field += left[field]

        if field == start:
            raise CycleError("unable to join cycles")

        if field in invalid_fields:
            continue

        neighbors = {field + direction for direction in _admissible_directions(field)}

        if neighbors & fields == set():
            continue

        break

    end = field + left[field]

    left[field] = (_admissible_directions(field) - {left[field]}).pop()
    start_right = field + left[field]

    if start_right not in right:
        raise ValueError("sth went terrible wrong. This cannot actually happen.")

    field = start_right

    while True:
        left[field] = right[field]

        if field + left[field] == start_right:
            break

        field += left[field]

    left[field] = end.diff(field)

    left.is_valid_or_raise()
    return left


class CycleAI:
    def __init__(self, board: Board):
        self.board = board
        self.position = board.snake.head
        self.cycle = HamiltonianCycle(*board.shape)

    def next(self) -> Direction:
        return self.cycle[self.head]

    @property
    def snake(self):
        return self.board.snake

    @property
    def head(self):
        return self.snake.head

    def optimize(self):
        apple = self.board.apple
        field = self.head

        print(f"field:    {field}")
        print(f"distance: {self.cycle.dist(field, apple)}")
        directions = _admissible_directions(field) - {self.cycle[field]}
        directions = {d for d in directions if field + d in self.board}

        if directions == set():
            print(f"    next: {field}: only one way to go")
            return

        direction = directions.pop()

        if self.board[field + direction] == Content.SNAKE:
            print(f"    next: {field}: snake in the way, ")
            return

        if self.cycle.dist(field + direction, apple) >= self.cycle.dist(
            field + self.cycle[field], apple
        ):
            print(f"    next: {field}: way got longer")
            return

        succesful = self.split_and_join(field)

        if not succesful:
            print(f"    next: {field}: couldn't split and join")
            return

        return

    def split_and_join(self, field: Field) -> bool:
        apple = self.board.apple

        cycle1, cycle2 = self.cycle.split(field)
        assert field in cycle1
        assert apple in cycle1

        invalid_fields = list(
            self.board.snake
        )  # TODO: not necessary to add whole snake

        _field = self.snake.head
        while True:
            _field += cycle1[_field]
            if _field == apple:
                break
            invalid_fields.append(_field)
        try:
            cycle = join_adjoint_cycles(cycle1, cycle2, apple, invalid_fields)
        except CycleError:
            return False

        if cycle.dist(field, apple) < self.cycle.dist(field, apple):
            self.cycle = HamiltonianCycle.from_cycle(cycle)
            return True
        return False


class SnakeAIv3(BaseAI):
    def search_best_direction(self) -> Direction:
        field = self.head
        visited: list[Field] = []

        if len(self._directions) == self.apple.dist(field):
            return self._directions.popleft()

        self._directions = deque([])

        try:
            self._search(field, self.apple, self.snake.direction, visited)
        except StopSearch:
            return self._directions.popleft()
        else:
            return self.stay_alive()

    def _search(
        self, start: Field, goal: Field, direction: Direction, visited: list[Field]
    ) -> None:
        if start == goal:
            raise StopSearch

        visited.append(start)

        directions = self._get_admissible_directions(start) - {direction.opposite()}
        directions &= self._get_alive_directions(start)
        directions &= self._get_unvisited_directions(start, visited)

        # directions = sorted(
        #     directions,
        #     key=lambda d: (d == direction)
        #     and (self.apple.dist(self.head) < self.apple.dist(self.head + d)),
        # )
        # directions = sorted(directions, key=lambda d: self.apple.dist(start + d))
        for _direction in self._sort_directions(start, direction, directions):
            self._directions.append(_direction)
            self._search(start + _direction, goal, _direction, visited=visited)
            _ = self._directions.pop()

    def _get_admissible_directions(self, field: Field) -> set[Direction]:
        return {
            Direction.DOWN if field.col % 2 == 0 else Direction.UP,
            Direction.RIGHT if field.row % 2 == 0 else Direction.LEFT,
        }

    def _get_alive_directions(self, field: Field) -> set[Direction]:
        return {
            direction
            for direction in Direction
            if (field + direction in self.board)
            and (self.board[field + direction] != Content.SNAKE)
        }

    def _get_unvisited_directions(self, field: Field, visited: list[Field]):
        return {
            direction for direction in Direction if field + direction not in visited
        }

    def stay_alive(self):
        print("Staying alive!")
        directions = self._get_admissible_directions(self.head)
        directions -= {self.snake.direction.opposite()}
        directions &= self._get_alive_directions(self.head)
        return directions.pop()

    def _sort_directions(
        self, field: Field, cur_direction: Direction, directions: set[Direction]
    ) -> list[Direction]:
        def distance(direction: Direction) -> int:
            return self.apple.dist(field + direction)

        def sort_by_direction(direction: Direction) -> int:
            if direction == cur_direction:
                return 0
            if distance(direction) < self.apple.dist(field):
                return -1
            if distance(direction) > self.apple.dist(field):
                return 1
            return 0

        return sorted(sorted(directions, key=sort_by_direction), key=distance)
