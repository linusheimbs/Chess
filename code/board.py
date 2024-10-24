import pygame

from settings import *
from pieces import Piece


class Board:
    def __init__(self, images):
        self.display_surface = pygame.display.get_surface()
        self.square = [None] * 64
        self.images = images

        # special rules
        self.pawn_promotion = None
        self.en_passant_target = None
        self.half_move = 0
        self.full_move = 0
        self.all_pieces = pygame.sprite.Group()
        self.white_pieces = pygame.sprite.Group()
        self.black_pieces = pygame.sprite.Group()

    def create_pieces_from_fen(self, squares):
        """ Initializes chess pieces on the board from a list of piece names or None values """
        for index, piece in enumerate(squares):
            pos = (index % 8, index // 8)
            if piece:
                self.square[index] = (Piece(piece, self.images[piece],
                                            (self.all_pieces, self.white_pieces if piece.split('_')[0] == 'white'
                                            else self.black_pieces), pos,
                                            self.white_pieces if piece.split('_')[0] == 'white' else self.black_pieces,
                                            self.black_pieces if piece.split('_')[0] == 'white' else self.white_pieces))

    def make_move(self, piece, new_col, new_row, legal_moves):
        """ Handles the move logic for a piece """
        if (new_col, new_row) in legal_moves:
            old_col = piece.pos[0] // TILE_SIZE
            old_row = piece.pos[1] // TILE_SIZE
            target_piece = self.square[new_row * 8 + new_col]
            old_position = (old_col, old_row)

            # If valid, finalize the move
            piece.pos = (new_col * TILE_SIZE, new_row * TILE_SIZE)
            piece.pos = piece.pos
            piece.rect.topleft = piece.pos
            self.square[old_position[1] * 8 + old_position[0]] = None  # Clear old position
            self.square[new_row * 8 + new_col] = piece  # Update to new position
            if not piece.has_moved:
                piece.has_moved = True

            # Castling
            if piece.type == 'king':
                if abs(new_col - old_col) == 2:  # Tries to castle
                    self.handle_castling(new_col, old_col, old_row)

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

    def handle_castling(self, new_col, old_col, old_row):
        """ Handles the rook placement of the castling logic """
        # Determine right castling
        if new_col - old_col == 2:
            rook_col = 7  # Always column 7
            rook_target_col = old_col + 1  # Rook moves to the column next to the king
        # Determine left castling
        elif new_col - old_col == -2:
            rook_col = 0  # Always column 0
            rook_target_col = old_col - 1  # Rook moves to the column next to the king
        else:
            return
        # Move the rook if it exists and is a rook
        rook = self.square[old_row * 8 + rook_col]
        if rook and rook.type == 'rook':
            # Move the rook to the target position next to the king
            rook.pos = (rook_target_col * TILE_SIZE, old_row * TILE_SIZE)
            rook.rect.topleft = rook.pos
            self.square[old_row * 8 + rook_col] = None  # Clear old rook position
            self.square[old_row * 8 + rook_target_col] = rook  # Place rook in the new position

    def promote_pawn(self, promotion_type):
        """ Handles the replacement of the promoting pawn with the new piece """
        # Get the variables of the pawn
        col, row = self.pawn_promotion.pos[0] // TILE_SIZE, self.pawn_promotion.pos[1] // TILE_SIZE
        pos = (col, row)
        name = f"{self.pawn_promotion.color}_{promotion_type}"
        surf = self.images[name]

        # Replace the pawn with the selected piece
        if self.pawn_promotion.color == 'white':
            new_piece = Piece(name, surf, (self.all_pieces, self.white_pieces), pos,
                              self.white_pieces, self.black_pieces)
            self.white_pieces.add(new_piece)
        else:
            new_piece = Piece(name, surf, (self.all_pieces, self.black_pieces), pos,
                              self.black_pieces, self.white_pieces)
            self.black_pieces.add(new_piece)

        # Update the board
        self.square[row * 8 + col] = new_piece
        self.all_pieces.add(new_piece)

        # Clear the pawn promotion flag and the piece
        self.pawn_promotion.kill()
        self.pawn_promotion = None

    def draw_board(self):
        """ Draw the rectangles of the board """
        for col in range(DIMENSION):
            for row in range(DIMENSION):
                color = COLORS['board_light'] if (col + row) % 2 == 0 else COLORS['board_dark']
                x = TILE_SIZE * row
                y = TILE_SIZE * col
                rect = pygame.rect.FRect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.display_surface, color, rect)
