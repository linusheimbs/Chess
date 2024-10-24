import pygame
from settings import *
from support import load_images, load_position_from_fen
from board import Board
from pieces import Piece
from button import Button
from ai import AI


class Engine:
    def __init__(self, player_color, vs_ai):
        # pygame setup
        self.running = True
        self.display_surface = pygame.display.get_surface()

        # general setup
        self.player_color = player_color
        self.white_to_move = True
        self.selected_piece = None
        self.fen_history = []
        self.fen_history.append(START_FEN_WHITE if self.player_color == 'white' else START_FEN_BLACK)
        self.setup()

        # ai
        self.vs_ai = vs_ai
        if self.vs_ai:
            self.ai = AI('black' if self.player_color == 'white' else 'white', self)
        self.ai_turn = False if self.player_color == 'white' else True

        # moves
        self.legal_moves = None

        # Fonts
        self.font = pygame.font.SysFont('Arial', 20)

        # Define scaling factors based on window height
        button_width = int(WINDOW_WIDTH * 0.2)  # Each button takes
        button_gap = int(WINDOW_WIDTH * 0.04)  # Gap between buttons
        button_height = int(WINDOW_HEIGHT * 0.1)  # Each button takes 10% of the screen height

        # Create promotion buttons dynamically based on window size
        self.promotion_buttons = {
            'queen': Button(button_gap, button_height, button_width, button_height,
                            "Promote to Queen", self.font, COLORS['button'], COLORS['button_hover'], 'white'),
            'rook': Button(2 * button_gap + button_width, button_height, button_width, button_height,
                           "Promote to Rook", self.font, COLORS['button'], COLORS['button_hover'], 'white'),
            'knight': Button(3 * button_gap + 2 * button_width, button_height, button_width, button_height,
                             "Promote to Knight", self.font, COLORS['button'], COLORS['button_hover'], 'white'),
            'bishop': Button(4 * button_gap + 3 * button_width, button_height, button_width, button_height,
                             "Promote to Bishop", self.font, COLORS['button'], COLORS['button_hover'], 'white')
        }

        # fen
        self.K_castle = True
        self.Q_castle = True
        self.k_castle = True
        self.q_castle = True

    def setup(self):
        """ Loads images and initializes the board and pieces from the starting FEN """
        self.images = load_images('..', 'graphics', 'pieces')

        # create the board
        self.board = Board(self.images)
        # create Pieces
        squares = load_position_from_fen(self.fen_history[0])
        self.board.create_pieces_from_fen(squares)

    def draw(self):
        """ Renders the game board, highlights, and pieces on the display surface """
        self.board.draw_board()
        self.draw_highlights()
        self.draw_pieces()
        if self.board.pawn_promotion:
            for button in self.promotion_buttons.values():
                button.draw(self.display_surface)

    def draw_highlights(self):
        """ Highlights the selected piece and its legal moves on the board """
        if self.selected_piece:
            rect = pygame.rect.FRect(self.selected_piece.pos[0], self.selected_piece.pos[1],
                                     TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.display_surface, 'orange', rect)
            for index, move in enumerate(self.legal_moves):
                rect = pygame.rect.FRect(move[0] * TILE_SIZE, move[1] * TILE_SIZE,
                                         TILE_SIZE, TILE_SIZE)
                color = COLORS['highlight_light'] if (move[0] + move[1]) % 2 == 0 else COLORS['highlight_dark']
                pygame.draw.rect(self.display_surface, color, rect)

    def draw_pieces(self):
        """ Draws all chess pieces on the board at their current positions """
        for piece in self.board.all_pieces:
            self.display_surface.blit(piece.surf, piece.rect)

    def handle_mouse_click(self, pos):
        if not self.ai_turn:
            """ Processes mouse click events for piece selection and promotion actions """
            if not self.board.pawn_promotion:
                for piece in self.board.all_pieces:
                    if piece.rect.collidepoint(pos):
                        if (self.white_to_move and 'white' in piece.color) or (
                                not self.white_to_move and 'black' in piece.color):
                            self.selected_piece = piece  # Select the piece
                            self.legal_moves = self.selected_piece.generate_legal_moves(
                                self.board.square, self.player_color, en_passant_target=self.board.en_passant_target)
                        break
            else:
                # Handle promotion selection
                for promotion_type, button in self.promotion_buttons.items():
                    if button.rect.collidepoint(pos):
                        self.board.promote_pawn(promotion_type)
                        # Switch turns
                        self.white_to_move = not self.white_to_move

                        # Generate new FEN and add to history
                        new_fen = self.generate_fen_from_board()
                        self.fen_history.append(new_fen)

                        if self.vs_ai:
                            self.ai_turn = not self.ai_turn
                        break

    def handle_mouse_move(self, pos):
        """ Updates the position of the selected piece based on mouse movement """
        if not self.board.pawn_promotion:
            if self.selected_piece:
                # get the mouse position
                x, y = (pos[0] - TILE_SIZE // 2, pos[1] - TILE_SIZE // 2)

                # constrain the x and y position to be within the window boundaries
                x = max(-TILE_SIZE//2, min(x, WINDOW_WIDTH - TILE_SIZE//2))
                y = max(-TILE_SIZE//2, min(y, WINDOW_HEIGHT - TILE_SIZE//2))

                # update the piece's position
                self.selected_piece.rect.topleft = (x, y)

    def handle_mouse_release(self, pos):
        """ Executes the move of the selected piece and updates the game state """
        if not self.board.pawn_promotion:
            if self.selected_piece:
                col = pos[0] // TILE_SIZE
                row = pos[1] // TILE_SIZE

                # Call the Board's make_move method
                if self.board.make_move(self.selected_piece, col, row, self.legal_moves):
                    # If the move is successful, handle any additional logic
                    if not self.board.pawn_promotion:
                        self.white_to_move = not self.white_to_move  # Switch turns
                        new_fen = self.generate_fen_from_board()
                        self.fen_history.append(new_fen)
                        if self.vs_ai:
                            self.ai_turn = not self.ai_turn
                else:
                    # Reset the piece's position if the move was invalid
                    self.selected_piece.rect.topleft = self.selected_piece.pos

                self.selected_piece = None  # Deselect the piece
                self.legal_moves = None

    def generate_fen_from_board(self):
        """ Generate a FEN string based on the current board state """
        fen = ""
        empty_count = 0

        # Board status
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
        if self.board.en_passant_target:
            file, rank = self.board.en_passant_target
            file = CHESS_NOTATION_WHITE[file] if self.player_color == 'white' else CHESS_NOTATION_BLACK[file]
            rank = 8 - rank if self.player_color == 'white' else rank + 1
            en_passant = f"{file}{rank}"
        else:  # No pawn eligible for en-passant
            en_passant = "-"
        fen += f" {en_passant}"
        # halfmove clock
        fen += f" {self.board.half_move}"
        # fullmove number
        fen += f" {self.board.full_move}"

        return fen

    def run(self):
        """ Main game loop that handles events and updates the display """
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

            if self.ai_turn:
                self.ai.make_move()
                self.ai_turn = False
                self.white_to_move = not self.white_to_move  # Switch turns
                new_fen = self.generate_fen_from_board()
                self.fen_history.append(new_fen)

            self.draw()

            pygame.display.flip()
