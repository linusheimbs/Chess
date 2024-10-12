import pygame

WINDOW_WIDTH = WINDOW_HEIGHT = 896
DIMENSION = 8
TILE_SIZE = WINDOW_WIDTH//DIMENSION
COLORS = {
    'board_light': '#f1d9c0',
    'board_dark': '#a97a65',
    'highlight_light': '#bc544b',
    'highlight_dark': '#710c04'
}

player_color = 'white'

START_FEN_BLACK = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
START_FEN_WHITE = 'RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr w KQkq - 0 1'
