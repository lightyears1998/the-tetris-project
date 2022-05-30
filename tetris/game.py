import numpy as np
from enum import Enum
from game_piece import *
import copy

ROWS = 20
COLS = 10


class GameStatus(Enum):
    RUNNING = 1
    TERMINATED = 0


class GameState:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.status = GameStatus.RUNNING
        self.score = 0
        self.frozen_blocks = np.zeros((rows, columns), dtype=np.int)
        self.frozen_blocks_color_code = np.zeros((rows, columns), dtype=np.int)
        self.falling_blocks = np.zeros((rows, columns), dtype=np.int)
        self.falling_blocks_color_code = np.zeros((rows, columns), dtype=np.int)
        self.falling_piece = PIECE_O
        self.falling_piece_location = np.zeros(2, dtype=np.int)
        self.next_falling_piece = None

    def numpy(self):
        return np.vstack((self.frozen_blocks, self.falling_blocks)).reshape((-1, self.rows, self.columns))

    @property
    def blocks(self):
        return self.frozen_blocks | self.falling_blocks

    @property
    def color_codes(self):
        return self.frozen_blocks_color_code + self.falling_blocks_color_code


def is_piece_hit_bottom_or_other_blocks(state: GameState):
    row, col = state.falling_piece_location
    for i in range(SHAPE_BOX_SIZE):
        for j in range(SHAPE_BOX_SIZE):
            if state.falling_piece.shape[i * SHAPE_BOX_SIZE + j] == 1:
                if row + i + 1 >= state.rows:
                    return True
                if state.frozen_blocks[row + i + 1][col + j] != 0:
                    return True
    return False


def detect_out_of_boundary_or_collision(frozen_blocks: np.ndarray, falling_piece: Piece, falling_piece_location: np.ndarray) -> bool:
    # @todo detects out of boundary

    row, col = falling_piece_location
    falling_piece_shape = falling_piece.shape
    for i in range(SHAPE_BOX_SIZE):
        for j in range(SHAPE_BOX_SIZE):
            if falling_piece_shape[i * SHAPE_BOX_SIZE + j] == 1 and frozen_blocks[row + i][col + j] == 1:
                return True
    return False


def update_falling_blocks(state: GameState):
    state.falling_blocks[:, :] = 0
    state.falling_blocks_color_code[:, :] = 0

    if state.falling_piece:
        row, col = state.falling_piece_location
        for i in range(SHAPE_BOX_SIZE):
            for j in range(SHAPE_BOX_SIZE):
                if state.falling_piece.shape[i * SHAPE_BOX_SIZE + j] == 1:
                    state.falling_blocks[row + i, col + j] = 1
                    state.falling_blocks_color_code[row + i, col + j] = state.falling_piece.color


def froze_falling_piece(state: GameState):
    row, col = state.falling_piece_location
    for i in range(SHAPE_BOX_SIZE):
        for j in range(SHAPE_BOX_SIZE):
            if state.falling_piece.shape[i * SHAPE_BOX_SIZE + j] == 1:
                state.frozen_blocks[row + i][col + j] = 1
                state.frozen_blocks_color_code[row + i][col + j] = state.falling_piece.color


def generate_next_falling_piece(state: GameState):
    piece = get_random_piece()
    state.next_falling_piece = piece


def stage_next_falling_piece(state: GameState):
    attempt = 0
    conflict = False
    stage_location = None

    while attempt < SHAPE_BOX_SIZE:
        stage_location = np.array([0 - attempt, (COLS - SHAPE_BOX_SIZE) / 2], dtype=np.int)
        conflict = detect_out_of_boundary_or_collision(state.frozen_blocks, state.next_falling_piece, stage_location)
        if not conflict:
            break
        attempt = attempt + 1

    if conflict:
        state.falling_piece = None
        update_falling_blocks(state)
        return False

    state.falling_piece = state.next_falling_piece
    state.falling_piece_location[:] = stage_location
    update_falling_blocks(state)
    return True


def move_piece_down(state: GameState):
    state.falling_piece_location[0] = state.falling_piece_location[0] + 1
    update_falling_blocks(state)


def remove_complete_lines(state: GameState):
    return 0


def new_game():
    state = GameState(ROWS, COLS)
    generate_next_falling_piece(state)
    stage_next_falling_piece(state)
    generate_next_falling_piece(state)
    update_falling_blocks(state)
    return state


def step(state: GameState):
    piece_has_hit_bottom_or_other_blocks = is_piece_hit_bottom_or_other_blocks(state)
    if piece_has_hit_bottom_or_other_blocks:
        froze_falling_piece(state)
        remove_complete_lines(state)
        stage_ok = stage_next_falling_piece(state)
        generate_next_falling_piece(state)
        if not stage_ok:
            state.status = GameStatus.TERMINATED
    else:
        move_piece_down(state)


def test_game():
    state = new_game()
    for i in range(1, 1000):
        print("======== No. ", i, "========")
        print(state.numpy())

        if state.status == GameStatus.TERMINATED:
            return
        step(state)


if __name__ == "__main__":
    test_game()
