from os.path import join
from os import walk
from settings import *


def load_images(*path):
    """ Loads and scales images from the specified directory into a dictionary """
    frames = {}
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image_name in image_names:
            full_path = join(folder_path, image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            surf = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
            frames[image_name.split('.')[0]] = surf
    return frames


def load_position_from_fen(fen):
    """ Converts a FEN string into a list representing piece positions on the board """
    piece_type_from_symbol = {
        'k': 'king',
        'p': 'pawn',
        'n': 'knight',
        'b': 'bishop',
        'r': 'rook',
        'q': 'queen'
    }

    fen_board = fen.split(' ')[0]
    file = 0
    rank = 7
    squares = [None] * 64  # 64 Felder auf einem Schachbrett

    for symbol in fen_board:
        if symbol == '/':
            file = 0
            rank -= 1
        elif symbol.isdigit():
            file += int(symbol)
        else:
            piece_colour = 'white' if symbol.isupper() else 'black'
            piece_type = piece_type_from_symbol[symbol.lower()]
            piece_name = f'{piece_colour}_{piece_type}'
            squares[rank * 8 + file] = piece_name
            file += 1

    return squares
