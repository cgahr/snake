__all__ = [
    "BOARD_SIZE",
    "FIELD_PX",
    "GAP_PX",
    "BORDER_PX",
    "WINSIZE",
    "FRAMES_PER_MOVE",
]

BOARD_SIZE: tuple[int, int] = (40, 20)
FIELD_PX: int = 30
GAP_PX: int = 5
BORDER_PX: int = 100
WINSIZE: tuple[int, int] = tuple(
    map(lambda x: x * FIELD_PX + (x - 1) * GAP_PX + 2 * BORDER_PX, BOARD_SIZE)
)  # type: ignore

FRAMES_PER_MOVE: int = 1
