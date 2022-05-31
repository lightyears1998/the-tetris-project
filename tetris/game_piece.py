from enum import Enum
import random
import copy

from color import Color

SHAPE_BOX_SIZE = 4

SHAPE_NONE = [
    [0, 0, 0, 0,
     0, 0, 0, 0,
     0, 0, 0, 0,
     0, 0, 0, 0],
]

SHAPE_I = [
    [0, 1, 0, 0,
     0, 1, 0, 0,
     0, 1, 0, 0,
     0, 1, 0, 0],
    [0, 0, 0, 0,
     1, 1, 1, 1,
     0, 0, 0, 0,
     0, 0, 0, 0]
]

SHAPE_O = [
    [0, 0, 0, 0,
     0, 1, 1, 0,
     0, 1, 1, 0,
     0, 0, 0, 0],
]

SHAPE_L = [
    [0, 1, 0, 0,
     0, 1, 0, 0,
     0, 1, 1, 0,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 1, 1, 1,
     0, 1, 0, 0,
     0, 0, 0, 0],
    [0, 1, 1, 0,
     0, 0, 1, 0,
     0, 0, 1, 0,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 0, 1, 0,
     1, 1, 1, 0,
     0, 0, 0, 0],
]

SHAPE_J = [
    [0, 0, 1, 0,
     0, 0, 1, 0,
     0, 1, 1, 0,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 1, 0, 0,
     0, 1, 1, 1,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 1, 1, 0,
     0, 1, 0, 0,
     0, 1, 0, 0],
    [0, 0, 0, 0,
     1, 1, 1, 0,
     0, 0, 1, 0,
     0, 0, 0, 0],
]

SHAPE_T = [
    [0, 0, 0, 0,
     0, 1, 0, 0,
     1, 1, 1, 0,
     0, 0, 0, 0],
    [0, 1, 0, 0,
     0, 1, 1, 0,
     0, 1, 0, 0,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 1, 1, 1,
     0, 0, 1, 0,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 0, 1, 0,
     0, 1, 1, 0,
     0, 0, 1, 0],
]

SHAPE_S = [
    [0, 0, 0, 0,
     0, 1, 1, 0,
     1, 1, 0, 0,
     0, 0, 0, 0],
    [0, 1, 0, 0,
     0, 1, 1, 0,
     0, 0, 1, 0,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 0, 1, 1,
     0, 1, 1, 0,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 1, 0, 0,
     0, 1, 1, 0,
     0, 0, 1, 0],
]


SHAPE_Z = [
    [0, 0, 0, 0,
     1, 1, 0, 0,
     0, 1, 1, 0,
     0, 0, 0, 0],
    [0, 0, 1, 0,
     0, 1, 1, 0,
     0, 1, 0, 0,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 1, 1, 0,
     0, 0, 1, 1,
     0, 0, 0, 0],
    [0, 0, 0, 0,
     0, 0, 1, 0,
     0, 1, 1, 0,
     0, 1, 0, 0],
]


class Piece:
    def __init__(self, shapes, color):
        self.shapes = shapes
        self.rotation = 0
        self.color = color

    @property
    def shape(self):
        return self.shapes[self.rotation]


PIECE_NONE = Piece(SHAPE_NONE, Color.WHITE)
PIECE_I = Piece(SHAPE_I, Color.LIGHT_BLUE)
PIECE_O = Piece(SHAPE_O, Color.YELLOW)
PIECE_L = Piece(SHAPE_L, Color.ORANGE)
PIECE_J = Piece(SHAPE_J, Color.BLUE)
PIECE_T = Piece(SHAPE_T, Color.PURPLE)
PIECE_S = Piece(SHAPE_S, Color.GREEN)
PIECE_Z = Piece(SHAPE_Z, Color.RED)

PIECES = [PIECE_I, PIECE_O, PIECE_L, PIECE_J, PIECE_T, PIECE_S, PIECE_Z]


def get_random_piece():
    candidate = copy.copy(random.choice(PIECES))
    candidate.rotation = random.randint(0, len(candidate.shapes) - 1)
    return candidate
