from collections import deque
from typing import Callable, Optional

from .dtypes import Content
from .exceptions import StopSearch
from .game import Board, Direction, Field, Snake


class BaseAI:
    def __init__(self, board: Board):
        self.board = board
        self._directions: deque[Direction] = deque([])

    @property
    def apple(self) -> Field:
        return self.board.apple

    @property
    def snake(self) -> Snake:
        return self.board.snake

    @property
    def head(self) -> Field:
        return self.snake.head

    @property
    def directions(self):
        return self._directions


class SnakeAI(BaseAI):
    def search_best_direction(self) -> Optional[Direction]:
        field = self.head
        visited: list[Field] = []

        if len(self._directions) == self.apple.dist(field):
            return self._directions.popleft()

        self._directions = deque([])

        try:
            self._search(field, self.apple, self.snake.direction, visited)
        except StopSearch:
            # print("there you are")
            return self._directions.popleft()
        else:
            return None
            # pass
            # print("Ohhhh no")

    def _search(
        self, start: Field, goal: Field, direction: Direction, visited: list[Field]
    ) -> None:
        if start == goal:
            raise StopSearch

        visited.append(start)

        directions = list(
            filter(
                lambda d: (d != direction.opposite())
                and (start + d not in visited)
                and (start + d in self.board)
                and (self.board[start + d] != Content.SNAKE),
                Direction,
            )
        )

        directions = sorted(
            directions,
            key=lambda d: 1
            if (d == direction)
            and (self.apple.dist(start + direction.opposite()) < self.apple.dist(start))
            else 0,
        )
        directions = sorted(directions, key=lambda d: self.apple.dist(start + d))
        for _direction in directions:
            self._directions.append(_direction)
            self._search(start + _direction, goal, _direction, visited=visited)
            _ = self._directions.pop()


class SnakeAIv2(BaseAI):
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
