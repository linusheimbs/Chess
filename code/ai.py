import random
from board import Board
from pieces import Piece
from settings import *


class AI:
    PIECE_VALUES = {
        'pawn': 1, 'knight': 3, 'bishop': 3, 'rook': 5, 'queen': 9, 'king': 100000,
    }

    def __init__(self, color, engine, depth=2):
        """ Initialize AI with the color it will play (white or black) and the engine instance """
        self.color = color
        self.engine = engine  # Reference to the game engine to access board state, FEN, etc.
        self.depth = depth
        self.pos_evaluated_count = 0

    def copy_board(self, board):
        """Creates a new board with pieces at the same positions as the current board"""
        new_board = Board(self.engine.board.images)  # Create a new board instance

        new_board.square = [None] * 64

        # Iterate through the original board's pieces and replicate them on the new board
        for index, piece in enumerate(board.square):
            if piece:
                pos = (index % 8, index // 8)
                new_piece = Piece(
                    name=f"{piece.color}_{piece.type}",
                    surf=piece.surf,
                    group=(new_board.all_pieces, new_board.white_pieces if piece.color == 'white'
                           else new_board.black_pieces),
                    pos=pos,
                    allied_pieces=new_board.white_pieces if piece.color == 'white' else new_board.black_pieces,
                    opponent_pieces=new_board.black_pieces if piece.color == 'white' else new_board.white_pieces)
                new_board.square[index] = new_piece

        # Copy other important attributes like castling rights, en passant, etc.
        new_board.pawn_promotion = board.pawn_promotion
        new_board.en_passant_target = board.en_passant_target
        new_board.half_move = board.half_move
        new_board.full_move = board.full_move

        return new_board

    def evaluate_board(self, board):
        """ Evaluate the board based on material values of the pieces """
        self.pos_evaluated_count += 1
        score = 0
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = board.square[row * 8 + col]
                if piece:
                    # Add value of piece, negative for opponent pieces
                    piece_value = self.PIECE_VALUES[piece.type]
                    if piece.color == self.color:
                        score += piece_value
                    else:
                        score -= piece_value
        return score

    def find_best_move(self):
        all_chosen_moves = []  # List to store all chosen moves (only moves)

        # Iterate over each piece of the current color
        for piece in self.engine.board.white_pieces if self.color == 'white' else self.engine.board.black_pieces:
            # Generate legal moves for the piece
            legal_moves = piece.generate_legal_moves(self.engine.board.square,
                                                     'white' if self.color == 'black' else 'black')

            # If there are legal moves available for the piece
            if legal_moves:
                # Choose a random move from the legal moves
                chosen_move = random.choice(legal_moves)
                all_chosen_moves.append(chosen_move)  # Add only the chosen move to the list

        # If no moves were chosen, return None (or some default value)
        if not all_chosen_moves:
            return None, None, []  # or handle this case as you see fit

        # Randomly select one of the chosen moves
        best_move = random.choice(all_chosen_moves)

        # Find the piece that made the best_move (if needed)
        best_piece = None
        for piece in self.engine.board.white_pieces if self.color == 'white' else self.engine.board.black_pieces:
            if best_move in piece.generate_legal_moves(self.engine.board.square,
                                                       'white' if self.color == 'black' else 'black'):
                best_piece = piece
                break  # Exit once we find the piece that can make this move

        return best_piece, best_move, all_chosen_moves  # Return the selected piece, move, and all chosen moves

    def make_move(self):
        """ Execute the best move found by the AI """
        best_piece, best_move, legal_moves = self.find_best_move()
        if best_piece and best_move:
            self.engine.board.make_move(best_piece, best_move[0], best_move[1], legal_moves)
        print(self.pos_evaluated_count)
        self.pos_evaluated_count = 0
