import pygame

pygame.init()

WINDOW_WIDTH = WINDOW_HEIGHT = 896
DIMENSION = 8
TILE_SIZE = WINDOW_WIDTH//DIMENSION
COLORS = {
    'board_light': '#f1d9c0',
    'board_dark': '#a97a65',
    'highlight_light': '#bc544b',
    'highlight_dark': '#710c04',
    'button': '#323232',
    'button_hover': '#646464'
}

START_FEN_BLACK = 'rnbkqbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBKQBNR w KQkq - 0 1'
START_FEN_WHITE = 'RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr w KQkq - 0 1'

CHESS_NOTATION_WHITE = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
CHESS_NOTATION_BLACK = {7: 'a', 6: 'b', 5: 'c', 4: 'd', 3: 'e', 2: 'f', 1: 'g', 0: 'h'}
