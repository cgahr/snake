#!/usr/bin/env python
import random
import time

import pygame as pg

from .ai import BaseAI, SnakeAI, SnakeAIv2
from .ai_cycle import SnakeAI as CycleAI
from .config import BOARD_SIZE, FRAMES_PER_MOVE, WINSIZE
from .dtypes import Color, Content, Direction
from .exceptions import LoseError, WinError
from .game import Board


def find_connected_regions():
    pass


def draw_board(surface, board):
    for field, content in board.items():
        if content == Content.EMPTY:
            _ = surface.fill(Color.GREY.value, field.rect)
        elif content == Content.SNAKE:
            _ = surface.fill(Color.GREEN.value, field.rect)
        else:
            _ = surface.fill(Color.RED.value, field.rect)


def draw_ai_path(surface, ai: BaseAI):
    field = ai.head

    if len(ai.directions) == 0:
        return

    for direction in list(ai.directions)[:-1]:
        field += direction
        _ = surface.fill(Color.LIGHTYELLOW.value, field.rect)


def draw_cycle_ai(surface, ai: CycleAI):
    apple = ai.board.apple
    position = ai.position
    position += ai.next()

    while position != apple:
        _ = surface.fill(Color.LIGHTYELLOW.value, position.rect)
        position += ai.next()


def set_text(text, x, y, fontSize):
    font = pg.font.Font("freesansbold.ttf", fontSize)

    text = font.render(text, True, Color.LIGHTGREY.value, Color.GREY.value)
    rect = text.get_rect()
    rect.center = (x, y)
    return (text, rect)


def main():
    random.seed()
    clock = pg.time.Clock()
    board = Board(BOARD_SIZE)

    pg.init()
    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("Snake")

    screen.fill(Color.BLACK.value)
    draw_board(screen, board)

    done = False
    frame_counter = 0

    # snake_ai = SnakeAIv2(board)
    cycle_ai = CycleAI(board)

    try:
        while not done:
            if frame_counter == 0:
                for event in pg.event.get():
                    if event.type == pg.KEYUP:
                        if event.key in (pg.K_UP, pg.K_w):
                            board.snake.turn(Direction.UP)
                        elif event.key in (pg.K_DOWN, pg.K_s):
                            board.snake.turn(Direction.DOWN)
                        elif event.key in (pg.K_LEFT, pg.K_a):
                            board.snake.turn(Direction.LEFT)
                        elif event.key in (pg.K_RIGHT, pg.K_d):
                            board.snake.turn(Direction.RIGHT)
                        break

                    if event.type == pg.QUIT:
                        done = True
                        break
                # start = time.time()
                # direction = snake_ai.search_best_direction()
                # print(f"{1000 * (time.time() - start):.3f}")
                direction = cycle_ai.next()
                board.snake.turn(direction)

                board.update()
                draw_board(screen, board)
                cycle_ai.cycle.draw(screen)
                # draw_ai_path(screen, snake_ai)
                # draw_cycle_ai(screen, cycle_ai)

                pg.display.update()
            clock.tick(80)
            frame_counter = (frame_counter + 1) % FRAMES_PER_MOVE
    except LoseError:
        text_with_coords = set_text("You lose!", WINSIZE[0] // 2, WINSIZE[1] // 2, 48)
        screen.blit(*text_with_coords)
        pg.display.update()
    except WinError:
        text_with_coords = set_text("You win!", WINSIZE[0] // 2, WINSIZE[1] // 2, 48)
        screen.blit(*text_with_coords)
        pg.display.update()

    pg.event.set_allowed(pg.QUIT)
    pg.event.set_allowed(pg.KEYUP)
    _ = pg.event.wait(100000)


if __name__ == "__main__":
    main()
