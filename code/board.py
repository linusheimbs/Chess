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

    def make_move(self, piece, new_col, new_row):
        """Handles the move logic for a piece."""
        # Validate the move
        if not self.validate_move(piece, new_col, new_row):
            return False  # Invalid move

        # Simulate the move
        old_position, target_piece = self.simulate_move(piece, new_col, new_row)

        # If valid, finalize the move
        piece.original_pos = (new_col * TILE_SIZE, new_row * TILE_SIZE)
        piece.rect.topleft = piece.original_pos
        self.square[old_position[1] * 8 + old_position[0]] = None  # Clear old position
        self.square[new_row * 8 + new_col] = piece  # Update to new position

        if target_piece:
            target_piece.kill()  # Handle captured piece

        return True  # Move successfully made

    def simulate_move(self, piece, new_col, new_row):
        """Simulate a move and check the board state."""
        # Store old position and target piece
        old_col = piece.original_pos[0] // TILE_SIZE
        old_row = piece.original_pos[1] // TILE_SIZE
        target_piece = self.square[new_row * 8 + new_col]
        return (old_col, old_row), target_piece

    def validate_move(self, piece, new_col, new_row):
        """Check if the move is legal for the selected piece."""
        # Generate legal moves for the piece
        legal_moves, threatened_pieces = piece.generate_legal_moves(self.square)

        # Check if the target position is in the legal moves
        if (new_col, new_row) not in legal_moves:
            return False  # Move is invalid
        return True

    def revert_move(self, piece, old_position, new_col, new_row, target_piece):
        """ Revert the simulated move """
        # Move the piece back to the old position
        old_col, old_row = old_position
        self.square[old_row * 8 + old_col] = piece
        self.square[new_row * 8 + new_col] = target_piece  # Restore the target piece, if any
        piece.original_pos = (old_col * TILE_SIZE, old_row * TILE_SIZE)

    def is_square_threatened(self, square, opponent_pieces):
        """Check if the given square is under attack by any of the opponent's pieces."""
        col, row = square
        for piece in opponent_pieces:
            moves, _ = piece.generate_legal_moves(self.square)
            if (col, row) in moves:
                return True  # The square is under attack
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
