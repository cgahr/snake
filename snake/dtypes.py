import enum

__all__ = [
    "Color",
    "Content",
    "Direction",
]


class Color(enum.Enum):
    BLACK = 0, 0, 0
    GREEN = 0, 255, 0
    GREY = 32, 32, 32
    LIGHTGREY = 100, 100, 100
    LIGHTYELLOW = 100, 100, 0
    RED = 255, 0, 0


class Content(enum.Enum):
    EMPTY = enum.auto()
    SNAKE = enum.auto()
    APPLE = enum.auto()

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"


class Direction(enum.Enum):
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    UP = (0, 1)
    DOWN = (0, -1)

    def opposite(self):
        return Direction((-self.value[0], -self.value[1]))

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"
