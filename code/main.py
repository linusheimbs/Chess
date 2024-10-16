import pygame.event
from settings import *
from support import load_images, load_position_from_fen
from board import Board
from pieces import Piece


class Main:
    def __init__(self):
        # pygame setup
        pygame.init()
        self.running = True
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Chess')

        # general setup
        self.white_to_move = True
        self.selected_piece = None
        self.fen_history = []
        self.fen_history.append(START_FEN_WHITE if player_color == 'white' else START_FEN_BLACK)
        self.setup()

        # moves
        self.legal_moves = None

    def setup(self):
        self.images = load_images('..', 'graphics', 'pieces')
        self.all_pieces = pygame.sprite.Group()
        self.white_pieces = pygame.sprite.Group()
        self.black_pieces = pygame.sprite.Group()

        # create the board
        self.board = Board()
        # create Pieces
        squares = load_position_from_fen(self.fen_history[0])
        self.board.create_pieces_from_fen(squares, (self.all_pieces, self.white_pieces, self.black_pieces), self.images)

    def draw(self):
        self.board.draw_board()
        self.draw_highlights()
        self.draw_pieces()

    def draw_highlights(self):
        if self.selected_piece:
            rect = pygame.rect.FRect(self.selected_piece.original_pos[0], self.selected_piece.original_pos[1],
                                     TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.display_surface, 'orange', rect)
            for index, move in enumerate(self.legal_moves):
                rect = pygame.rect.FRect(move[0] * TILE_SIZE, move[1] * TILE_SIZE,
                                         TILE_SIZE, TILE_SIZE)
                color = COLORS['highlight_light'] if (move[0] + move[1]) % 2 == 0 else COLORS['highlight_dark']
                pygame.draw.rect(self.display_surface, color, rect)

    def draw_pieces(self):
        for piece in self.all_pieces:
            self.display_surface.blit(piece.surf, piece.rect)

    def handle_mouse_click(self, pos):
        for piece in self.all_pieces:
            if piece.rect.collidepoint(pos):
                if (self.white_to_move and 'white' in piece.color) or (
                        not self.white_to_move and 'black' in piece.color):
                    self.selected_piece = piece  # Select the piece
                    self.legal_moves, _ = self.selected_piece.generate_legal_moves(self.board.square)
                break

    def handle_mouse_move(self, pos):
        if self.selected_piece:
            # get the mouse position
            x, y = (pos[0] - TILE_SIZE // 2, pos[1] - TILE_SIZE // 2)

            # constrain the x and y position to be within the window boundaries
            x = max(-TILE_SIZE//2, min(x, WINDOW_WIDTH - TILE_SIZE//2))
            y = max(-TILE_SIZE//2, min(y, WINDOW_HEIGHT - TILE_SIZE//2))

            # update the piece's position
            self.selected_piece.rect.topleft = (x, y)

    def handle_mouse_release(self, pos):
        if self.selected_piece:
            col = pos[0] // TILE_SIZE
            row = pos[1] // TILE_SIZE

            # Call the Board's make_move method
            if self.board.make_move(self.selected_piece, col, row, self.legal_moves):
                # If the move is successful, handle any additional logic
                self.white_to_move = not self.white_to_move  # Switch turns
                new_fen = self.generate_fen_from_board()
                self.fen_history.append(new_fen)
            else:
                # Reset the piece's position if the move was invalid
                self.selected_piece.rect.topleft = self.selected_piece.original_pos

            self.selected_piece = None  # Deselect the piece
            self.legal_moves = None

    def generate_fen_from_board(self):
        """Generate a FEN string based on the current board state"""
        fen = ""
        empty_count = 0

        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = self.board.square[row * 8 + col]

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
        fen += f" KQkq"
        # en passant
        fen += f" -"
        # halfmove clock
        fen += f" 0"
        # fullmove number
        fen += f" 1"

        return fen

    def run(self):
        while self.running:
            self.display_surface.fill('black')

            # event handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left mouse button
                        self.handle_mouse_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left mouse button
                        self.handle_mouse_release(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_move(event.pos)

            self.draw()

            pygame.display.flip()


if __name__ == '__main__':
    main = Main()
    main.run()
