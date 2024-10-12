import pygame.sprite
import copy

from settings import *


class Piece(pygame.sprite.Sprite):
    def __init__(self, name, surf, group, pos, allied_pieces, opponent_pieces):
        super().__init__(group)
        self.pos = (pos[0]*TILE_SIZE,pos[1]*TILE_SIZE)
        self.original_pos = self.pos
        self.color = name.split('_')[0]
        self.type = name.split('_')[1]
        self.group = group
        self.allied_pieces = allied_pieces
        self.opponent_pieces = opponent_pieces
        self.surf = surf
        self.rect = surf.get_rect(topleft=self.pos)
        self.has_moved = False

    def __repr__(self):
        return f'{self.color} {self.type}'

    def generate_legal_moves(self, board, skip_check=False):
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
                legal_moves, target_piece = self.generate_king_moves(board)
            case 'pawn':
                legal_moves, target_piece = self.generate_pawn_moves(board)
            case _:
                legal_moves, target_piece = [], None

        if skip_check:
            return legal_moves, target_piece  # Skip further check validation

        removed_moves = []
        for move in legal_moves:
            new_board = create_shallow_board_copy(board, self, move)
            old_col = self.original_pos[0] // TILE_SIZE
            old_row = self.original_pos[1] // TILE_SIZE

            if new_board[move[0] * 8 + move[1]]:
                new_board[move[0] * 8 + move[1]] = None  # Clear captured piece
            new_board[old_col * 8 + old_row] = None  # Clear old position
            new_board[move[0] * 8 + move[1]] = self  # Update to new position

            # Check if the move places the king in check
            if is_king_in_check(new_board, self.opponent_pieces, self.allied_pieces):
                removed_moves.append(move)

        # Remove move if king would be in check
        for move in removed_moves:
            legal_moves.remove(move)

        return legal_moves, target_piece

    def generate_rook_moves(self, board):
        """ Generate legal moves for the rook """
        col, row = self.original_pos[0] // TILE_SIZE, self.original_pos[1] // TILE_SIZE
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
        col, row = self.original_pos[0] // TILE_SIZE, self.original_pos[1] // TILE_SIZE
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
        col, row = self.original_pos[0] // TILE_SIZE, self.original_pos[1] // TILE_SIZE
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

    def generate_pawn_moves(self, board):
        """ Generate legal moves for the pawn """
        # pawn movement logic depends on whether it's a white or black pawn
        col, row = self.original_pos[0] // TILE_SIZE, self.original_pos[1] // TILE_SIZE
        direction = -1 if 'white' in self.color else 1  # white moves up, black moves down (needs changes later)
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
                if potential_target and potential_target.color != self.color:
                    legal_moves.append((new_col, row + direction))
                    target_pieces.append(potential_target)

        return legal_moves, target_pieces

    def generate_king_moves(self, board):
        """ Generate legal moves for the king """
        col, row = self.original_pos[0] // TILE_SIZE, self.original_pos[1] // TILE_SIZE
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

            # Castling Logic
            if not self.has_moved:  # Only allow castling if the king hasn't moved
                # Kingside castling (toward the right)
                kingside_rook_pos = 7  # Column 7 (H file)
                kingside_rook = board[row * 8 + kingside_rook_pos]
                if isinstance(kingside_rook, Piece) and kingside_rook.type == 'rook' and\
                        kingside_rook.color == self.color and not kingside_rook.has_moved:
                    # Check that the squares between king and rook are empty
                    if all(board[row * 8 + i] is None for i in range(col + 1, kingside_rook_pos)):
                        # The king can castle kingside
                        legal_moves.append((col + 2, row))

                # Queenside castling
                queenside_rook_pos = 0  # Column 0 (A file)
                queenside_rook = board[row * 8 + queenside_rook_pos]
                if isinstance(queenside_rook, Piece) and queenside_rook.type == 'rook' and\
                        queenside_rook.color == self.color and not queenside_rook.has_moved:
                    # Check that the squares between king and rook are empty
                    if all(board[row * 8 + i] is None for i in range(queenside_rook_pos + 1, col)):
                        # The king can castle queenside
                        legal_moves.append((col - 2, row))

        return legal_moves, target_pieces

    def generate_queen_moves(self, board):
        """ Generate legal moves for the queen """
        col, row = self.original_pos[0] // TILE_SIZE, self.original_pos[1] // TILE_SIZE
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
    new_board = [None if piece is None else piece for piece in board]

    old_col = moving_piece.original_pos[0] // TILE_SIZE
    old_row = moving_piece.original_pos[1] // TILE_SIZE

    # Clear the old position and new position of the moving piece
    new_board[old_row * 8 + old_col] = None
    new_board[move[1] * 8 + move[0]] = None

    # Move the piece to the new position
    new_board[move[1] * 8 + move[0]] = moving_piece

    return new_board


def is_king_in_check(board, opponent_pieces, own_pieces, skip_check=False):
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
        legal_moves, _ = piece.generate_legal_moves(board, skip_check=True)
        if (king_pos[0], king_pos[1]) in legal_moves:
            return True  # The king is in check

    return False  # The king is safe