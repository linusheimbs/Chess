import pygame

from settings import *
from pieces import Piece


class Board:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.square = []

        # special rules
        self.pawn_promotion = None
        self.en_passant_target = None
        self.half_move = 0
        self.full_move = 0

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

            # If valid, finalize the move
            piece.original_pos = (new_col * TILE_SIZE, new_row * TILE_SIZE)
            piece.rect.topleft = piece.original_pos
            self.square[old_position[1] * 8 + old_position[0]] = None  # Clear old position
            self.square[new_row * 8 + new_col] = piece  # Update to new position
            if not piece.has_moved:
                piece.has_moved = True

            # Castling logic: Check if king moved two spaces horizontally
            if piece.type == 'king':
                # Kingside castling (king moves two spaces to the right)
                if new_col - old_col == 2:
                    # Find the rook at the right corner (column 7) of the same row
                    rook = self.square[old_row * 8 + 7]
                    if rook and rook.type == 'rook':
                        # Move the rook next to the king (to column 5)
                        rook.original_pos = (5 * TILE_SIZE, old_row * TILE_SIZE)
                        rook.rect.topleft = rook.original_pos
                        self.square[old_row * 8 + 7] = None  # Clear old rook position
                        self.square[old_row * 8 + 5] = rook  # Update new rook position
                # Queenside castling (king moves two spaces to the left)
                elif new_col - old_col == -2:
                    # Find the rook at the left corner (column 0) of the same row
                    rook = self.square[old_row * 8 + 0]
                    if rook and rook.type == 'rook':
                        # Move the rook next to the king (to column 3)
                        rook.original_pos = (3 * TILE_SIZE, old_row * TILE_SIZE)
                        rook.rect.topleft = rook.original_pos
                        self.square[old_row * 8 + 0] = None  # Clear old rook position
                        self.square[old_row * 8 + 3] = rook  # Update new rook position

            # Pawn en-passant or promotion
            if piece.type == 'pawn':
                if new_row == 0 or new_row == 7:
                    self.pawn_promotion = piece
                if self.en_passant_target and (new_col, new_row) == self.en_passant_target:  # If en-passant
                    target_col = self.en_passant_target[0]  # Column of the en passant target
                    target_row = new_row + (old_row - new_row)  # The row where the captured pawn resides
                    target_pos = target_row * 8 + target_col  # Convert (col, row) to board position index
                    target_piece = self.square[target_pos]  # The captured pawn
                    self.square[target_pos] = None  # Clear captured pawn position
                    self.en_passant_target = None
                if abs(new_row - old_row) == 2:  # Check if pawn moved two squares forward
                    target_row = (old_row + new_row) // 2  # The row between the start and end position
                    self.en_passant_target = (new_col, target_row)  # Set en passant target position
                else:
                    self.en_passant_target = None
            else:
                self.en_passant_target = None  # Reset if no en passant is possible

            # Change counting variables
            if piece.type == 'pawn' or target_piece:
                self.half_move = 0
            else:
                self.half_move += 1
            if piece.color == 'white':
                self.full_move += 1

            # Capturing and special moves
            if target_piece:
                if target_piece.color != piece.color:
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
