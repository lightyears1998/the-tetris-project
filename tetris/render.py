import sys
import numpy as np
import pygame
import torch
from color import *
from game import *

pygame.init()

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
FPS = 60


def draw_text(surface: pygame.Surface, text: str, text_size = 16):
    font = pygame.font.SysFont("Consolas", size=text_size)
    bitmap = font.render(text, True, COLOR_MAPPING[Color.BLACK])
    blit_left = (surface.get_width() - bitmap.get_width()) / 2
    blit_top = (surface.get_height() - bitmap.get_height()) / 2
    surface.blit(bitmap, (blit_left, blit_top))


def render_blocks():
    pass


def draw_tetris_container(surface: pygame.Surface, state: GameState):
    grid_size = 20
    gap_width = 4

    container_width = (COLS + 1) * gap_width + COLS * grid_size
    container_height = (ROWS + 1) * gap_width + ROWS * grid_size

    container_pos_left = (surface.get_width() - container_width) / 2
    container_pos_top = (surface.get_height() - container_height) / 2

    # horizontal lines
    for row in range(ROWS + 1):
        start_pos = (container_pos_left, container_pos_top + row * (gap_width + grid_size))
        end_pos = (container_pos_left + container_width, container_pos_top + row * (gap_width + grid_size))
        pygame.draw.line(surface, COLOR_MAPPING[Color.GREY], start_pos, end_pos, width=gap_width)

    # vertical lines
    for col in range(COLS + 1):
        start_pos = (container_pos_left + col * (grid_size + gap_width), container_pos_top)
        end_pos = (container_pos_left + col * (grid_size + gap_width), container_pos_top + container_height)
        pygame.draw.line(surface, COLOR_MAPPING[Color.GREY], start_pos, end_pos, width=gap_width)

    # grids
    blocks = state.blocks
    color_codes = state.color_codes
    for row in range(ROWS):
        for col in range(COLS):
            if blocks[row, col] == 1:
                left = container_pos_left + gap_width + col * (gap_width + grid_size)
                top = container_pos_top + gap_width + row * (gap_width + grid_size)
                width = grid_size
                height = grid_size
                rect = pygame.Rect(left, top, width, height)
                color = COLOR_MAPPING[color_codes[row, col]]
                pygame.draw.rect(surface, color, rect)
    if state.status == GameStatus.TERMINATED:
        draw_text(surface, "Game over", 64)


def render():
    screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
    pygame.display.set_caption("Tetris")

    clock = pygame.time.Clock()
    state = new_game()

    frame_count = 0
    run = True
    while run:
        clock.tick(FPS)
        frame_count = (frame_count + 1) % FPS

        if frame_count % 2 == 0:
            if state.status == GameStatus.RUNNING:
                step(state)

        screen.fill(COLOR_MAPPING[Color.WHITE])
        draw_text(screen.subsurface((0, 0, WINDOW_WIDTH, 64)), "score: " + format(state.score))
        draw_tetris_container(screen.subsurface((0, 64, WINDOW_WIDTH, WINDOW_HEIGHT - 64)), state)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                print(event)

    pygame.quit()


if __name__ == "__main__":
    render()
