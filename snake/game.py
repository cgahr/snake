import random
from collections import deque
from typing import Optional

import pygame as pg

from .config import BORDER_PX, FIELD_PX, GAP_PX, WINSIZE
from .dtypes import Content, Direction
from .exceptions import LoseError, WinError


class Field:
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self._rect = None

    def __eq__(self, other):
        return (self.col == other.col) and (self.row == other.row)

    def __sub__(self, other: Direction):
        if not isinstance(other, Direction):
            raise ValueError("You can only subtract 'Direction' from 'Field'!")

        return Field(self.col - other.value[0], self.row - other.value[1])

    def __add__(self, other: Direction):
        if not isinstance(other, Direction):
            raise ValueError("You can only add 'Direction' to 'Field'!")

        return Field(self.col + other.value[0], self.row + other.value[1])

    def __hash__(self):
        return hash((self.col, self.row))

    def __str__(self):
        return f"Field(col={self.col}, row={self.row})"

    def __repr__(self):
        return f"Field(col={self.col}, row={self.row})"

    def dist(self, other):
        return abs(self.col - other.col) + abs(self.row - other.row)

    def diff(self, other):
        if self.dist(other) != 1:
            raise ValueError(
                f"the distance between both fields must be 1, it is {self.dist(other)}."
            )

        return Direction((self.col - other.col, self.row - other.row))

    @property
    def rect(self) -> pg.Rect:
        if self._rect is None:
            left = BORDER_PX + self.col * FIELD_PX + self.col * GAP_PX
            top = (
                WINSIZE[1] - BORDER_PX - ((self.row + 1) * FIELD_PX + self.row * GAP_PX)
            )
            width = FIELD_PX
            height = FIELD_PX
            self._rect = pg.Rect(left, top, width, height)
        return self._rect


class Snake(deque[Field]):
    def __init__(self, pos: Field, direction: Direction = Direction.LEFT):
        super().__init__([pos, pos - direction])
        self.direction = direction

    def __iter(self):
        super().__iter__()

    def move(self) -> tuple[Field, Field]:
        field = self.next_field()
        if field in self:
            raise LoseError

        self.appendleft(field)
        empty = self.pop()
        return field, empty

    def grow(self) -> Field:
        field = self.next_field()
        self.appendleft(field)
        return field

    def next_field(self) -> Field:
        return self.head + self.direction

    @property
    def head(self) -> Field:
        return self[0]

    def turn(self, direction: Optional[Direction]):
        if (direction is not None) and (self.direction.opposite() != direction):
            self.direction = direction

    def admissible_directions(self):
        pass


class Board(dict[Field, Content]):
    apple: Field
    snake: Snake

    def __init__(self, shape: tuple[int, int]):
        self.shape = shape

        super().__init__(
            {
                Field(col, row): Content.EMPTY
                for col in range(shape[0])
                for row in range(shape[1])
            }
        )

        self.init_snake()

        apple = self.new_apple()
        # apple = Field(self.shape[0] // 2 + 3, self.shape[1] // 2)
        # self.apple = apple
        self[apple] = Content.APPLE

    def init_snake(self):
        self.snake = Snake(Field(self.shape[0] // 2, self.shape[1] // 2))
        for field in self.snake:
            self[field] = Content.SNAKE

    def update(self):
        if self.snake.next_field() == self.apple:
            head = self.snake.grow()
            self[head] = Content.SNAKE

            apple = self.new_apple()
            self[apple] = Content.APPLE
        else:
            head, empty = self.snake.move()
            if head not in self:
                raise LoseError

            self[head] = Content.SNAKE
            self[empty] = Content.EMPTY

    def new_apple(self) -> Field:
        try:
            self.apple = random.choice(
                [key for key, value in self.items() if value is Content.EMPTY]
            )
            return self.apple
        except IndexError as err:
            raise WinError from err
