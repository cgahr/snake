from collections import deque
from itertools import product
from typing import Callable

import numpy as np
import pygame as pg

from .ai import BaseAI
from .config import FIELD_PX
from .dtypes import Color, Content
from .exceptions import InvalidCycleError, NonAdjacentCyclesError, StopSearch
from .game import Board, Direction, Field, Snake


def _admissible_directions(field: Field) -> set[Direction]:
    return {
        Direction.UP if field.col % 2 == 0 else Direction.DOWN,
        Direction.LEFT if field.row % 2 == 0 else Direction.RIGHT,
    }


# dict[Field, Direction]
class Cycle:
    def __init__(self, fields: tuple[Field, ...], directions: tuple[Direction, ...]):
        self.__data = {field: direction for field, direction in zip(fields, directions)}
        self.is_valid_or_raise()

    def __getitem__(self, field: Field):
        return self.__data[field]

    def __setitem__(self, field: Field, direction):
        self.__data[field] = direction

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __str__(self):
        return str(self.__data)

    def __repr__(self):
        return repr(self.__data)

    # def copy(self):
    #     return self.__init__(self.__data.keys(), self.__data.values())

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
        cur = start
        dist = 0
        while cur != end:
            cur += self[cur]
            dist += 1

            if cur == end:
                return dist
            if cur == start:
                return np.nan
        raise InvalidCycleError()

    def is_valid_or_raise(self):
        copy = self.__data.copy()

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

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    def items(self):
        return self.__data.items()

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
        directions = (Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT)
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

        super().__init__(cycle.keys(), cycle.values())

    def _fields_from_start_with_directions(
        self, field: Field, directions: tuple[Direction, ...]
    ) -> tuple[Field, ...]:
        fields = [field]

        for direction in directions:
            fields.append(fields[-1] + direction)
        return tuple(fields)


class SnakeAI:
    def __init__(self, board: Board):
        self.board = board
        self.position = board.snake.head
        self.cycle = HamiltonianCycle(*board.shape)

    def next(self) -> Direction:
        direction = self.cycle[self.position]
        self.position += direction
        return direction

    def optimize(self):
        raise NotImplementedError


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
