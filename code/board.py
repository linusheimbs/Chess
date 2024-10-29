import pygame

from settings import *
from pieces import Piece
from support import is_king_in_check


class Board:
    def __init__(self, images, player_color, starting_pos):
        self.display_surface = pygame.display.get_surface()
        self.square = [None] * 64
        self.images = images

        # groups
        self.all_pieces = pygame.sprite.Group()
        self.white_pieces = pygame.sprite.Group()
        self.black_pieces = pygame.sprite.Group()

        # essential
        self.player_color = player_color
        self.white_to_move = True

        # special rules and fen variables
        self.pawn_promotion = None
        self.en_passant_target = None
        self.half_move = 0
        self.full_move = 0
        self.K_castle = True
        self.Q_castle = True
        self.k_castle = True
        self.q_castle = True

        # game over
        self.checkmate = False
        self.game_drawn = False

        # fen
        self.fen_history = []

        # create Pieces
        self.load_and_create_pieces_from_fen(starting_pos)

    def load_and_create_pieces_from_fen(self, fen):
        """ Converts a FEN string into a list representing piece positions on the board and initializes the pieces """
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

        # Load positions from the FEN string
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

        # Create pieces on the board from the loaded positions
        for index, piece in enumerate(squares):
            pos = (index % 8, index // 8)
            if piece:
                self.square[index] = (Piece(piece, self.images[piece],
                                            (self.all_pieces,
                                             self.white_pieces if piece.split('_')[
                                                                      0] == 'white' else self.black_pieces),
                                            pos,
                                            self.white_pieces if piece.split('_')[0] == 'white' else self.black_pieces,
                                            self.black_pieces if piece.split('_')[0] == 'white' else self.white_pieces))

        self.fen_history.append(fen)

    def generate_fen_from_board(self):
        """ Generate a FEN string based on the current board state """
        fen = ""
        empty_count = 0

        # Board status
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = self.square[row * 8 + col]

                if piece is None:
                    empty_count += 1  # count empty squares
                else:
                    if empty_count > 0:
                        fen += str(empty_count)  # add empty squares count to FEN
                        empty_count = 0

                    piece_type = piece.type[0]  # first letter of the piece type (r, n, b, q, k, p)
                    if 'white' in piece.type:
                        fen += piece_type.upper()  # uppercase for white pieces
                    else:
                        fen += piece_type.lower()  # lowercase for black pieces

            if empty_count > 0:
                fen += str(empty_count)  # append remaining empty squares count
                empty_count = 0

            if row != DIMENSION - 1:
                fen += "/"  # add row separator

        # turn
        turn = 'w' if self.white_to_move else 'b'
        fen += f" {turn}"
        # castling
        castling = ''
        if any([self.K_castle, self.Q_castle, self.k_castle, self.q_castle]):
            if self.K_castle:
                castling += 'K'
            if self.Q_castle:
                castling += 'Q'
            if self.k_castle:
                castling += 'k'
            if self.q_castle:
                castling += 'q'
        else:
            castling = '-'
        fen += f" {castling}"
        # en passant
        if self.en_passant_target:
            file, rank = self.en_passant_target
            file = CHESS_NOTATION_WHITE[file] if self.player_color == 'white' else CHESS_NOTATION_BLACK[file]
            rank = 8 - rank if self.player_color == 'white' else rank + 1
            en_passant = f"{file}{rank}"
        else:  # No pawn eligible for en-passant
            en_passant = "-"
        fen += f" {en_passant}"
        # halfmove clock
        fen += f" {self.half_move}"
        # fullmove number
        fen += f" {self.full_move}"

        return fen

    def generate_current_sides_moves(self):
        legal_moves = {}
        for piece in self.white_pieces if self.white_to_move else self.black_pieces:
            piece_legal_moves = piece.generate_legal_moves(
                self.square, 'black' if self.white_to_move else 'white', en_passant_target=self.en_passant_target)
            if piece_legal_moves:
                legal_moves[piece] = piece_legal_moves
        return legal_moves

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

            # Capturing
            if target_piece:
                if target_piece.color != piece.color:
                    target_piece.kill()  # Handle captured piece

            self.white_to_move = not self.white_to_move

            # Change counting variables
            if piece.type == 'pawn' or target_piece:
                self.half_move = 0
            else:
                self.half_move += 1
            if piece.color == 'white':
                self.full_move += 1

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

    def check_game_over(self):
        if not self.generate_current_sides_moves():
            if is_king_in_check(
                    self.square,
                    self.black_pieces if self.white_to_move else self.white_pieces,
                    self.white_pieces if self.white_to_move else self.black_pieces,
                    'white' if self.white_to_move else 'black'):
                self.checkmate = True
            else:
                self.game_drawn = True

    def draw_board(self):
        """ Draw the rectangles of the board """
        for col in range(DIMENSION):
            for row in range(DIMENSION):
                color = COLORS['board_light'] if (col + row) % 2 == 0 else COLORS['board_dark']
                x = TILE_SIZE * row
                y = TILE_SIZE * col
                rect = pygame.rect.FRect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.display_surface, color, rect)
