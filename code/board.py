import pygame.display

from settings import *
from pieces import Piece


class Board:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.square = []

    def create_pieces_from_fen(self, squares, group, piece_images):
        for index, piece in enumerate(squares):
            pos = (index % 8, index // 8)
            if piece:
                self.square.append(Piece(piece, piece_images[piece],
                                         (group[0], group[1 if piece.split('_')[0] == 'white' else 2]), pos,
                                         group[1 if piece.split('_')[0] == 'white' else 2],
                                         group[2 if piece.split('_')[0] == 'white' else 1]))
            else:
                self.square.append(piece)

    def make_move(self, piece, new_col, new_row, legal_moves):
        if (new_col, new_row) in legal_moves:
            """Handles the move logic for a piece."""
            old_col = piece.original_pos[0] // TILE_SIZE
            old_row = piece.original_pos[1] // TILE_SIZE
            target_piece = self.square[new_row * 8 + new_col]
            old_position = (old_col, old_row)

            # Castling check: king moves two spaces horizontally
            if piece.type == 'king':
                if new_col - old_col == 2:
                    print('castling ks')
                elif new_col - old_col == -2:
                    print('castling qs')

            # If valid, finalize the move
            piece.original_pos = (new_col * TILE_SIZE, new_row * TILE_SIZE)
            piece.rect.topleft = piece.original_pos
            self.square[old_position[1] * 8 + old_position[0]] = None  # Clear old position
            self.square[new_row * 8 + new_col] = piece  # Update to new position

            if target_piece:
                target_piece.kill()  # Handle captured piece

            return True  # Move successfully made
        else:
            return False

    def draw_board(self):
        """ Draw the rectangles of the board """
        for col in range(DIMENSION):
            for row in range(DIMENSION):
                color = COLORS['board_light'] if (col + row) % 2 == 0 else COLORS['board_dark']
                x = TILE_SIZE * row
                y = TILE_SIZE * col
                rect = pygame.rect.FRect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.display_surface, color, rect)
