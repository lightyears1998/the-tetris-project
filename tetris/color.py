from enum import IntEnum


class Color(IntEnum):
    WHITE = 0
    BLACK = 1
    LIGHT_BLUE = 2
    BLUE = 3
    ORANGE = 4
    YELLOW = 5
    GREEN = 6
    PURPLE = 7
    RED = 8
    GREY = 9


COLOR_MAPPING = {
    Color.WHITE: (255, 255, 255),
    Color.GREY: (220, 220, 220),
    Color.BLACK: (0, 0, 0),
    Color.LIGHT_BLUE: (0, 240, 240),
    Color.BLUE: (0, 0, 240),
    Color.ORANGE: (240, 160, 0),
    Color.YELLOW: (240, 240, 0),
    Color.GREEN: (0, 240, 0),
    Color.PURPLE: (160, 0, 240),
    Color.RED: (240, 0, 0),
}
