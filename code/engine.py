import pygame
from settings import *
from support import load_images, load_position_from_fen
from board import Board
from pieces import Piece
from button import Button
from text import draw_text_box
from ai import AI


class Engine:
    def __init__(self, player_color, vs_ai):
        # pygame setup
        self.running = True
        self.display_surface = pygame.display.get_surface()

        # general setup
        self.player_color = player_color
        self.selected_piece = None
        self.setup()

        # ai
        self.vs_ai = vs_ai
        if self.vs_ai:
            self.ai = AI('black' if self.player_color == 'white' else 'white', self)
        self.ai_turn = False if self.player_color == 'white' else True

        # moves
        self.legal_moves = None

        # Fonts
        self.font_promotion = pygame.font.SysFont('Arial', 20)
        self.font_text = pygame.font.SysFont('Arial', 50)

        # Define scaling factors based on window height
        button_width = int(WINDOW_WIDTH * 0.2)  # Each button takes
        button_gap = int(WINDOW_WIDTH * 0.04)  # Gap between buttons
        button_height = int(WINDOW_HEIGHT * 0.1)  # Each button takes 10% of the screen height

        # Create promotion buttons dynamically based on window size
        self.promotion_buttons = {
            'queen': Button(button_gap, button_height, button_width, button_height,
                            "Promote to Queen", self.font_promotion),
            'rook': Button(2 * button_gap + button_width, button_height, button_width, button_height,
                           "Promote to Rook", self.font_promotion),
            'knight': Button(3 * button_gap + 2 * button_width, button_height, button_width, button_height,
                             "Promote to Knight", self.font_promotion),
            'bishop': Button(4 * button_gap + 3 * button_width, button_height, button_width, button_height,
                             "Promote to Bishop", self.font_promotion),
        }
        self.exit_button = Button(WINDOW_WIDTH // 2 - button_width // 2, WINDOW_HEIGHT // 2 - button_height // 2,
                                  button_width, button_height, f"Exit", self.font_promotion)

    def setup(self):
        """ Loads images and initializes the board and pieces from the starting FEN """
        self.images = load_images('..', 'graphics', 'pieces')

        # create the board
        self.board = Board(self.images, self.player_color,
                           START_FEN_WHITE if self.player_color == 'white' else START_FEN_BLACK)

    def draw(self):
        """ Renders the game board, highlights, and pieces on the display surface """
        self.board.draw_board()
        self.draw_highlights()
        self.draw_pieces()
        if self.board.pawn_promotion:
            for button in self.promotion_buttons.values():
                button.draw(self.display_surface)
        elif self.board.checkmate or self.board.game_drawn:
            if self.board.checkmate:
                text = "White wins!" if not self.board.white_to_move else "Black wins!"
                draw_text_box(self.display_surface, text, (WINDOW_WIDTH//2, WINDOW_HEIGHT//3), self.font_text)
            elif self.board.game_drawn:
                text = "Draw!"
                draw_text_box(self.display_surface, text, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3), self.font_text)
            self.exit_button.draw(self.display_surface)

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
        if not self.ai_turn and not self.board.game_drawn and not self.board.checkmate:
            """ Processes mouse click events for piece selection and promotion actions """
            if not self.board.pawn_promotion:
                for piece in self.board.all_pieces:
                    if piece.rect.collidepoint(pos):
                        if (self.board.white_to_move and 'white' in piece.color) or (
                                not self.board.white_to_move and 'black' in piece.color):
                            self.selected_piece = piece  # Select the piece
                            self.legal_moves = self.selected_piece.generate_legal_moves(
                                self.board.square, self.player_color, en_passant_target=self.board.en_passant_target)
                        break
            else:
                # Handle promotion selection
                for promotion_type, button in self.promotion_buttons.items():
                    if button.rect.collidepoint(pos):
                        self.board.promote_pawn(promotion_type)

                        # Generate new FEN and add to history
                        new_fen = self.board.generate_fen_from_board()
                        self.board.fen_history.append(new_fen)

                        if self.vs_ai:
                            self.ai_turn = not self.ai_turn
                        if not self.board.checkmate and not self.board.game_drawn:
                            self.board.check_game_over()
                        break
        else:
            if self.exit_button.rect.collidepoint(pos):
                self.running = False

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
                        new_fen = self.board.generate_fen_from_board()
                        self.board.fen_history.append(new_fen)
                        if self.vs_ai:
                            self.ai_turn = not self.ai_turn
                        if not self.board.checkmate and not self.board.game_drawn:
                            self.board.check_game_over()
                else:
                    # Reset the piece's position if the move was invalid
                    self.selected_piece.rect.topleft = self.selected_piece.pos

                self.selected_piece = None  # Deselect the piece
                self.legal_moves = None

    def run(self):
        """ Main game loop that handles events and updates the display """
        while self.running:
            self.display_surface.fill('black')

            if self.ai_turn and not self.board.game_drawn and not self.board.checkmate:
                self.ai.make_move()
                if self.board.pawn_promotion:
                    self.board.promote_pawn('queen')
                self.ai_turn = False
                new_fen = self.board.generate_fen_from_board()
                self.board.fen_history.append(new_fen)
                if not self.board.checkmate and not self.board.game_drawn:
                    self.board.check_game_over()

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
