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
    squares = [None] * 64

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


def is_king_in_check(board, opponent_pieces, own_pieces, player_color, skip_check=False):
    """ Check if the king of the given color is in check """
    if skip_check:
        return False  # Skip checking for checks to avoid recursion

    king_pos = (0, 0)
    for col in range(8):
        for row in range(8):
            piece = board[row * 8 + col]
            if piece and piece.type == 'king' and piece in own_pieces:
                king_pos = (col, row)
                break

    # Check if any opponent piece threatens the king
    for piece in opponent_pieces:
        legal_moves = piece.generate_legal_moves(board, player_color, skip_check=True)
        if king_pos in legal_moves:
            return True  # The king is in check

    return False  # The king is safe
