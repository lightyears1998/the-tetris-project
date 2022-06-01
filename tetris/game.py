import numpy as np
from enum import Enum
from game_piece import *
import copy

GAME_ROWS = 20
GAME_COLS = 10
GAME_ACTIONS = 5


class GameStatus(Enum):
    RUNNING = 1
    TERMINATED = 0


class GameState:
    DATA_INDEX_FROZEN_BLOCKS = 0
    DATA_INDEX_FROZEN_BLOCKS_COLOR_CODE = 1
    DATA_INDEX_FALLING_BLOCKS = 2
    DATA_INDEX_FALLING_BLOCKS_COLOR_CODE = 3

    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.status = GameStatus.RUNNING
        self.score = 0
        self.op_left = 0
        self.op_right = 0
        self.op_rotate = 0
        self.op_soft_drop = 0
        self.op_hard_drop = 0
        self.single_line_cleared = 0
        self.double_lines_cleared = 0
        self.triple_lines_cleared = 0
        self.tetris_line_cleared = 0  # i.e. quadruple lines cleared
        self.soft_drop_distance = 0
        self.hard_drop_distance = 0
        self.data = np.zeros((4, rows, columns), dtype=np.int)
        self.falling_piece = PIECE_NONE
        self.falling_piece_location = np.zeros(2, dtype=np.int)
        self.next_falling_piece = PIECE_NONE

    def __str__(self):
        block_statistics = 'block_count: {}\tblock_fill_rate: {}\n'.format(self.block_count, self.block_fill_rate)
        op_statistics = 'op_left: {}\top_right: {}\top_rotate: {}\top_soft_drop: {}\top_hard_drop: {}\n'.format(
            self.op_left, self.op_right, self.op_rotate, self.op_soft_drop, self.op_hard_drop)
        line_statistics = 'single_line_cleared: {}\tdouble_lines_cleared: {}' \
                          '\ttriple_lines_cleared: {}\ttetris_line_cleared {}\n'.format(
                            self.single_line_cleared,
                            self.double_lines_cleared,
                            self.triple_lines_cleared,
                            self.tetris_line_cleared
        )
        distance_statistics = 'soft_drop_distance: {}\thard_drop_distance: {}'.format(
            self.soft_drop_distance, self.hard_drop_distance)
        return block_statistics + op_statistics + line_statistics + distance_statistics

    def numpy(self):
        return np.vstack((self.frozen_blocks, self.falling_blocks)).reshape((-1, self.rows, self.columns))

    @property
    def block_count(self):
        return np.sum(self.blocks)

    @property
    def block_fill_rate(self):
        return self.block_count / (GAME_ROWS * GAME_COLS)

    @property
    def frozen_blocks(self):
        return self.data[self.DATA_INDEX_FROZEN_BLOCKS]

    @property
    def frozen_blocks_color_code(self):
        return self.data[self.DATA_INDEX_FROZEN_BLOCKS_COLOR_CODE]

    @property
    def falling_blocks(self):
        return self.data[self.DATA_INDEX_FALLING_BLOCKS]

    @property
    def falling_blocks_color_code(self):
        return self.data[self.DATA_INDEX_FALLING_BLOCKS_COLOR_CODE]

    @property
    def blocks(self):
        return self.frozen_blocks | self.falling_blocks

    @property
    def color_codes(self):
        return self.frozen_blocks_color_code + self.falling_blocks_color_code


def is_piece_hitting_bottom_or_other_blocks(state: GameState):
    row, col = state.falling_piece_location
    for i in range(SHAPE_BOX_SIZE):
        for j in range(SHAPE_BOX_SIZE):
            if state.falling_piece.shape[i * SHAPE_BOX_SIZE + j] == 1:
                if row + i + 1 >= state.rows:
                    return True
                if state.frozen_blocks[row + i + 1][col + j] != 0:
                    return True
    return False


def detect_out_of_boundary_or_collision(frozen_blocks: np.ndarray, falling_piece: Piece,
                                        falling_piece_location: np.ndarray) -> bool:
    piece_row, piece_col = falling_piece_location
    falling_piece_shape = falling_piece.shape
    for i in range(SHAPE_BOX_SIZE):
        for j in range(SHAPE_BOX_SIZE):
            if falling_piece_shape[i * SHAPE_BOX_SIZE + j] == 1:
                row = piece_row + i
                col = piece_col + j
                if row < 0 or row >= GAME_ROWS:
                    return True
                if col < 0 or col >= GAME_COLS:
                    return True
                if frozen_blocks[row][col] == 1:
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
        stage_location = np.array([0 - attempt, (GAME_COLS - SHAPE_BOX_SIZE) / 2], dtype=np.int)
        conflict = detect_out_of_boundary_or_collision(state.frozen_blocks, state.next_falling_piece, stage_location)
        if not conflict:
            break
        attempt = attempt + 1

    if conflict:
        state.falling_piece = PIECE_NONE
        update_falling_blocks(state)
        return False

    state.falling_piece = state.next_falling_piece
    state.falling_piece_location[:] = stage_location
    update_falling_blocks(state)
    return True


def move_piece_down(state: GameState):
    state.falling_piece_location[0] = state.falling_piece_location[0] + 1
    update_falling_blocks(state)


def move_piece_left(state: GameState):
    state.falling_piece_location[1] = state.falling_piece_location[1] - 1
    update_falling_blocks(state)


def move_piece_right(state: GameState):
    state.falling_piece_location[1] = state.falling_piece_location[1] + 1
    update_falling_blocks(state)


def rotate_piece(state: GameState):
    state.falling_piece.rotation = (state.falling_piece.rotation + 1) % len(state.falling_piece.shapes)
    update_falling_blocks(state)


def drop_piece(state: GameState):
    move_distance = 0
    while not is_piece_hitting_bottom_or_other_blocks(state):
        move_piece_down(state)
        move_distance += 1
    update_falling_blocks(state)
    return move_distance


def user_move_piece_down(state: GameState):
    neo_location = state.falling_piece_location.copy()
    neo_location[0] = neo_location[0] + 1
    conflict = detect_out_of_boundary_or_collision(state.frozen_blocks, state.falling_piece, neo_location)
    if not conflict:
        move_piece_down(state)
        state.soft_drop_distance += 1
        state.op_soft_drop += 1
        state.score += 1


def user_move_piece_left(state: GameState):
    neo_location = state.falling_piece_location.copy()
    neo_location[1] = neo_location[1] - 1
    conflict = detect_out_of_boundary_or_collision(state.frozen_blocks, state.falling_piece, neo_location)
    if not conflict:
        move_piece_left(state)
        state.op_left += 1


def user_move_piece_right(state: GameState):
    neo_location = state.falling_piece_location.copy()
    neo_location[1] = neo_location[1] + 1
    conflict = detect_out_of_boundary_or_collision(state.frozen_blocks, state.falling_piece, neo_location)
    if not conflict:
        move_piece_right(state)
        state.op_right += 1


def user_rotate_piece(state: GameState):
    neo_piece = copy.copy(state.falling_piece)
    neo_piece.rotation = (neo_piece.rotation + 1) % len(neo_piece.shapes)
    conflict = detect_out_of_boundary_or_collision(state.frozen_blocks, neo_piece, state.falling_piece_location)
    if not conflict:
        rotate_piece(state)
        state.op_rotate += 1


def user_drop_piece(state: GameState):
    move_distance = drop_piece(state)
    if move_distance > 0:
        state.op_hard_drop += 1
        state.hard_drop_distance += move_distance
        state.score += move_distance * 2


def remove_complete_lines(state: GameState):
    removed_lines_count = 0
    blocks = state.frozen_blocks
    data = state.data

    row = GAME_ROWS - 1
    while row >= 0:
        while blocks[row].sum() == GAME_COLS:
            data[:, 1:row + 1] = data[:, 0:row]
            data[:, 0] = 0
            removed_lines_count = removed_lines_count + 1
        row = row - 1

    if removed_lines_count == 0:
        gained_score = 0
    elif removed_lines_count == 1:
        gained_score = 100
        state.single_line_cleared += 1
    elif removed_lines_count == 2:
        gained_score = 300
        state.double_lines_cleared += 1
    elif removed_lines_count == 3:
        gained_score = 500
        state.triple_lines_cleared += 1
    elif removed_lines_count == 4:
        gained_score = 800
        state.tetris_line_cleared += 1
    else:
        raise "TAKE A REST NOW! Clearing more than 4 lines at a single step is impossible."

    state.score = state.score + gained_score


def new_game():
    state = GameState(GAME_ROWS, GAME_COLS)
    generate_next_falling_piece(state)
    stage_next_falling_piece(state)
    generate_next_falling_piece(state)
    update_falling_blocks(state)
    return state


def step(state: GameState):
    if state.status == GameStatus.TERMINATED:
        return

    piece_has_hit_bottom_or_other_blocks = is_piece_hitting_bottom_or_other_blocks(state)
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
