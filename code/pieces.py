import pygame

from settings import *
from support import is_king_in_check


class Piece(pygame.sprite.Sprite):
    def __init__(self, name, surf, group, pos, allied_pieces, opponent_pieces):
        super().__init__(group)
        self.pos = (pos[0]*TILE_SIZE,pos[1]*TILE_SIZE)
        self.color = name.split('_')[0]
        self.type = name.split('_')[1]
        self.group = group
        self.allied_pieces = allied_pieces
        self.opponent_pieces = opponent_pieces
        self.surf = surf
        self.rect = surf.get_rect(topleft=self.pos)
        self.has_moved = False

    def __repr__(self):
        return f'{self.color.capitalize()}{self.type.capitalize()}'

    def generate_legal_moves(self, board, player_color, en_passant_target=None, skip_check=False):
        """ General method to route to the specific piece's move generation """
        piece_type = self.type
        match piece_type:
            case 'rook':
                legal_moves, target_piece = self.generate_rook_moves(board)
            case 'bishop':
                legal_moves, target_piece = self.generate_bishop_moves(board)
            case 'queen':
                legal_moves, target_piece = self.generate_queen_moves(board)
            case 'knight':
                legal_moves, target_piece = self.generate_knight_moves(board)
            case 'king':
                legal_moves, target_piece = self.generate_king_moves(board, player_color, skip_check)
            case 'pawn':
                legal_moves, target_piece = self.generate_pawn_moves(board, player_color, en_passant_target)
            case _:
                legal_moves, target_piece = [], None

        if skip_check:
            return legal_moves  # Skip further check validation

        removed_moves = []
        for move in legal_moves:
            new_board, captured_piece = create_shallow_board_copy(board, self, move)

            opponent_pieces = [p for p in self.opponent_pieces if p != captured_piece]

            # Check if the move places the king in check
            if is_king_in_check(new_board, opponent_pieces, self.allied_pieces, player_color):
                removed_moves.append(move)

        # Remove move if king would be in check
        for move in removed_moves:
            legal_moves.remove(move)

        return legal_moves

    def generate_rook_moves(self, board):
        """ Generate legal moves for the rook """
        col, row = self.pos[0] // TILE_SIZE, self.pos[1] // TILE_SIZE
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        legal_moves = []
        target_pieces = []

        for direction in directions:
            for i in range(1, DIMENSION):
                new_col = col + direction[0] * i
                new_row = row + direction[1] * i
                if 0 <= new_col < DIMENSION and 0 <= new_row < DIMENSION:
                    potential_target = board[new_row * 8 + new_col]
                    if not potential_target:
                        legal_moves.append((new_col, new_row))
                    elif potential_target.color != self.color:
                        legal_moves.append((new_col, new_row))
                        target_pieces.append(potential_target)
                        break
                    else:
                        break
                else:
                    break
        return legal_moves, target_pieces

    def generate_bishop_moves(self, board):
        """ Generate legal moves for the bishop """
        col, row = self.pos[0] // TILE_SIZE, self.pos[1] // TILE_SIZE
        directions = [(-1, -1), (1, 1), (-1, 1), (1, -1)]  # diagonal directions
        legal_moves = []
        target_pieces = []

        # move diagonal
        for direction in directions:
            for i in range(1, DIMENSION):
                new_col = col + direction[0] * i
                new_row = row + direction[1] * i
                if 0 <= new_col < DIMENSION and 0 <= new_row < DIMENSION:
                    potential_target = board[new_row * 8 + new_col]
                    if not potential_target:  # if empty
                        legal_moves.append((new_col, new_row))
                    elif potential_target.color != self.color:  # or capture enemy piece
                        legal_moves.append((new_col, new_row))
                        target_pieces.append(potential_target)
                        break
                    else:
                        break
                else:
                    break
        return legal_moves, target_pieces

    def generate_knight_moves(self, board):
        """ Generate legal moves for the knight """
        col, row = self.pos[0] // TILE_SIZE, self.pos[1] // TILE_SIZE
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]  # L-shapes
        legal_moves = []
        target_pieces = []

        # move in L shape
        for move in knight_moves:
            new_col = col + move[0]
            new_row = row + move[1]
            if 0 <= new_col < DIMENSION and 0 <= new_row < DIMENSION:
                potential_target = board[new_row * 8 + new_col]
                if not potential_target or potential_target.color != self.color:
                    legal_moves.append((new_col, new_row))
                    if potential_target:
                        target_pieces.append(potential_target)

        return legal_moves, target_pieces

    def generate_pawn_moves(self, board, player_color, en_passant_target):
        """ Generate legal moves for the pawn """
        # pawn movement logic depends on whether it's a white or black pawn
        col, row = self.pos[0] // TILE_SIZE, self.pos[1] // TILE_SIZE
        if ('white' in self.color and player_color == 'white') or ('black' in self.color and player_color == 'black'):
            direction = -1
        else:
            direction = 1
        legal_moves = []
        target_pieces = []

        # move one square forward
        if 0 <= row + direction < DIMENSION:
            if not board[(row + direction) * 8 + col]:  # if empty
                legal_moves.append((col, row + direction))

                # move two squares forward on first move
                if (row == 1 and direction == 1) or (row == 6 and direction == -1):
                    if not board[(row + 2 * direction) * 8 + col]:  # if also empty
                        legal_moves.append((col, row + 2 * direction))

        # capture diagonally
        for side in [-1, 1]:
            new_col = col + side
            if 0 <= new_col < DIMENSION and 0 <= row + direction < DIMENSION:
                potential_target = board[(row + direction) * 8 + new_col]
                if ((potential_target and potential_target.color != self.color)
                        or en_passant_target == (new_col, row + direction)):
                    legal_moves.append((new_col, row + direction))
                    target_pieces.append(potential_target)

        return legal_moves, target_pieces

    def generate_king_moves(self, board, player_color, skip_check=False):
        """ Generate legal moves for the king """
        col, row = self.pos[0] // TILE_SIZE, self.pos[1] // TILE_SIZE
        king_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1),
                      (1, -1)]  # all 8 directions, 1 square
        legal_moves = []
        target_pieces = []

        # move by one in all directions
        for move in king_moves:
            new_col = col + move[0]
            new_row = row + move[1]
            if 0 <= new_col < DIMENSION and 0 <= new_row < DIMENSION:
                potential_target = board[new_row * 8 + new_col]
                if not potential_target or potential_target.color != self.color:
                    legal_moves.append((new_col, new_row))
                    if potential_target:
                        target_pieces.append(potential_target)

        # Skip check
        if skip_check:
            return legal_moves, target_pieces

        # Castling Logic
        if not self.has_moved:  # Only allow castling if the king hasn't moved
            # Kingside castling (toward the right)
            kingside_rook_pos = 7  # Column 7 (H file)
            kingside_rook = board[row * 8 + kingside_rook_pos]
            kingside_castle_possible = []
            if kingside_rook and kingside_rook.type == 'rook' and\
                    kingside_rook.color == self.color and not kingside_rook.has_moved:
                # Check that the squares between king and rook are empty
                for i in range(col + 1, kingside_rook_pos):
                    kingside_castle_possible.append(board[row * 8 + i] is None)
                move = (col + 1, row)
                new_board, _ = create_shallow_board_copy(board, self, move)
                kingside_castle_possible.append(
                    not is_king_in_check(new_board, self.opponent_pieces, self.allied_pieces, player_color))
                if all(kingside_castle_possible):
                    # The king can castle kingside
                    legal_moves.append((col + 2, row))
                    target_pieces.append(kingside_rook)

            # Queenside castling
            queenside_rook_pos = 0  # Column 0 (A file)
            queenside_rook = board[row * 8 + queenside_rook_pos]
            queenside_castle_possible = []
            if queenside_rook and queenside_rook.type == 'rook' and\
                    queenside_rook.color == self.color and not queenside_rook.has_moved:
                # Check that the squares between king and rook are empty
                for i in range(queenside_rook_pos + 1, col):
                    queenside_castle_possible.append(board[row * 8 + i] is None)
                move = (col - 1, row)
                new_board, _ = create_shallow_board_copy(board, self, move)
                queenside_castle_possible.append(
                    not is_king_in_check(new_board, self.opponent_pieces, self.allied_pieces, player_color))
                if all(queenside_castle_possible):
                    # The king can castle queenside
                    legal_moves.append((col - 2, row))
                    target_pieces.append(queenside_rook)
        return legal_moves, target_pieces

    def generate_queen_moves(self, board):
        """ Generate legal moves for the queen """
        col, row = self.pos[0] // TILE_SIZE, self.pos[1] // TILE_SIZE
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]  # all 8 directions
        legal_moves = []
        target_pieces = []

        # move in all directions
        for direction in directions:
            for i in range(1, DIMENSION):
                new_col = col + direction[0] * i
                new_row = row + direction[1] * i
                if 0 <= new_col < DIMENSION and 0 <= new_row < DIMENSION:
                    potential_target = board[new_row * 8 + new_col]
                    if not potential_target:
                        legal_moves.append((new_col, new_row))
                    elif potential_target.color != self.color:
                        legal_moves.append((new_col, new_row))
                        target_pieces.append(potential_target)
                        break
                    else:
                        break
                else:
                    break

        return legal_moves, target_pieces


def create_shallow_board_copy(board, moving_piece, move):
    """ Creates a shallow copy of the board with the moving piece in its new position """
    new_board = [None if piece is None else piece for piece in board]

    old_col = moving_piece.pos[0] // TILE_SIZE
    old_row = moving_piece.pos[1] // TILE_SIZE

    # Clear the old position and new position of the moving piece
    new_board[old_row * 8 + old_col] = None
    captured_piece = new_board[move[0] + move[1] * 8]
    new_board[move[0] + move[1] * 8] = None

    # Move the piece to the new position
    new_board[move[0] + move[1] * 8] = moving_piece
    return new_board, captured_piece
