import sys
import numpy as np
import pygame
import torch
from color import *
from game import *

pygame.init()

FPS = 120

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600

GRID_SIZE = 20
GAP_WIDTH = 4


def draw_text(surface: pygame.Surface, text: str, text_size=16):
    font = pygame.font.SysFont("Consolas", size=text_size)
    bitmap = font.render(text, True, COLOR_MAPPING[Color.BLACK])
    blit_left = (surface.get_width() - bitmap.get_width()) / 2
    blit_top = (surface.get_height() - bitmap.get_height()) / 2
    surface.blit(bitmap, (blit_left, blit_top))


def draw_next_piece_hint(surface: pygame.Surface, state: GameState):
    gap_width = GAP_WIDTH / 2
    grid_size = GRID_SIZE / 2

    container_width = (SHAPE_BOX_SIZE + 1) * gap_width  + SHAPE_BOX_SIZE * grid_size
    container_height = container_width

    container_pos_left = (surface.get_width() - container_width) / 2
    container_pos_top = (surface.get_height() - container_height) / 2

    if state.next_falling_piece:
        shape = state.next_falling_piece.shape
        color = COLOR_MAPPING[state.next_falling_piece.color]
        for row in range(SHAPE_BOX_SIZE):
            for col in range(SHAPE_BOX_SIZE):
                if shape[row * SHAPE_BOX_SIZE + col] != 0:
                    left = container_pos_left + gap_width + col * (gap_width + grid_size)
                    top = container_pos_top + gap_width + row * (gap_width + grid_size)
                    width = grid_size
                    height = grid_size
                    rect = pygame.Rect(left, top, width, height)
                    pygame.draw.rect(surface, color, rect)


def draw_tetris_container(surface: pygame.Surface, state: GameState):
    container_width = (COLS + 1) * GAP_WIDTH + COLS * GRID_SIZE
    container_height = (ROWS + 1) * GAP_WIDTH + ROWS * GRID_SIZE

    container_pos_left = (surface.get_width() - container_width) / 2
    container_pos_top = (surface.get_height() - container_height) / 2

    # horizontal lines
    for row in range(ROWS + 1):
        start_pos = (container_pos_left, container_pos_top + row * (GAP_WIDTH + GRID_SIZE))
        end_pos = (container_pos_left + container_width, container_pos_top + row * (GAP_WIDTH + GRID_SIZE))
        pygame.draw.line(surface, COLOR_MAPPING[Color.GREY], start_pos, end_pos, width=GAP_WIDTH)

    # vertical lines
    for col in range(COLS + 1):
        start_pos = (container_pos_left + col * (GRID_SIZE + GAP_WIDTH), container_pos_top)
        end_pos = (container_pos_left + col * (GRID_SIZE + GAP_WIDTH), container_pos_top + container_height)
        pygame.draw.line(surface, COLOR_MAPPING[Color.GREY], start_pos, end_pos, width=GAP_WIDTH)

    # grids
    blocks = state.blocks
    color_codes = state.color_codes
    for row in range(ROWS):
        for col in range(COLS):
            if blocks[row, col] == 1:
                left = container_pos_left + GAP_WIDTH + col * (GAP_WIDTH + GRID_SIZE)
                top = container_pos_top + GAP_WIDTH + row * (GAP_WIDTH + GRID_SIZE)
                width = GRID_SIZE
                height = GRID_SIZE
                rect = pygame.Rect(left, top, width, height)
                color = COLOR_MAPPING[color_codes[row, col]]
                pygame.draw.rect(surface, color, rect)
    if state.status == GameStatus.TERMINATED:
        draw_text(surface, "Game Over", 64)


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

        if frame_count % 60 == 0:
            if state.status == GameStatus.RUNNING:
                step(state)

        screen.fill(COLOR_MAPPING[Color.WHITE])
        draw_text(screen.subsurface((0, 0, WINDOW_WIDTH / 2, 64)), "score: " + format(state.score))
        draw_next_piece_hint(screen.subsurface((WINDOW_WIDTH / 2, 0, WINDOW_WIDTH / 2, 64)), state)
        draw_tetris_container(screen.subsurface((0, 64, WINDOW_WIDTH, WINDOW_HEIGHT - 64)), state)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_SPACE:
                    drop_piece(state)
                elif key == pygame.K_RIGHT:
                    user_move_piece_right(state)
                elif key == pygame.K_LEFT:
                    user_move_piece_left(state)
                elif key == pygame.K_UP:
                    user_rotate_piece(state)
                elif key == pygame.K_DOWN:
                    user_move_piece_down(state)

    pygame.quit()


if __name__ == "__main__":
    render()
