import pygame
from settings import *
from engine import Engine
from button import Button  # Import the Button class


class Main:
    def __init__(self):
        # Window setup
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Chess')

        # General attributes
        self.running = True
        self.state = 'menu'  # Default state
        self.player_color = 'white'
        self.vs_ai = False  # Whether the player is playing against the AI

        # Fonts
        self.menu_font = pygame.font.SysFont('Arial', 32)

        # Define button dimensions based on window size
        button_width = int(WINDOW_WIDTH * 0.33)  # 33% of the window width
        button_height = int(WINDOW_HEIGHT * 0.1)  # 10% of the window height
        button_gap = int(WINDOW_HEIGHT * 0.05)  # 5% gap between buttons

        # Create buttons for play and exit options
        self.play_button = Button(button_width, 3 * button_height, button_width, button_height,'Play',
                                  self.menu_font, COLORS['button'], COLORS['button_hover'], 'white')

        self.exit_button = Button(button_width, button_gap + 4 * button_height, button_width, button_height,'Exit',
                                  self.menu_font, COLORS['button'], COLORS['button_hover'], 'white')

        # Buttons for game mode selection
        self.pvp_button = Button(button_width, 3 * button_height, button_width, button_height,
                                 'Player vs Player', self.menu_font, COLORS['button'], COLORS['button_hover'], 'white')
        self.pve_button = Button(button_width, button_gap + 4 * button_height, button_width, button_height,
                                 'Player vs AI', self.menu_font, COLORS['button'], COLORS['button_hover'], 'white')

        # Color selection buttons
        self.white_button = Button(button_width, 3 * button_height, button_width, button_height,
                                   'Play as White', self.menu_font, COLORS['button'], COLORS['button_hover'], 'white')
        self.black_button = Button(button_width, button_gap + 4 * button_height, button_width, button_height,
                                   'Play as Black', self.menu_font, COLORS['button'], COLORS['button_hover'],'white')

        # Back button
        self.back_button = Button(button_width, 2 * button_gap + 5 * button_height, button_width, button_height,
                                  'Back', self.menu_font, COLORS['button'], COLORS['button_hover'], 'white')

        # Placeholder for the game engine
        self.engine = None

    def draw_menu(self):
        """Draw the main menu with buttons"""
        self.display_surface.fill('black')
        self.play_button.draw(self.display_surface)
        self.exit_button.draw(self.display_surface)

    def draw_game_mode_menu(self):
        """Draw the game mode selection menu"""
        self.display_surface.fill('black')
        self.pvp_button.draw(self.display_surface)
        self.pve_button.draw(self.display_surface)
        self.back_button.draw(self.display_surface)

    def draw_color_selection_menu(self):
        """Draw the color selection menu"""
        self.display_surface.fill('black')
        self.white_button.draw(self.display_surface)
        self.black_button.draw(self.display_surface)
        self.back_button.draw(self.display_surface)

    def handle_menu_input(self, event):
        """Handle button clicks in the main menu"""
        if self.play_button.is_clicked(event):
            self.state = 'game_mode_menu'
        elif self.exit_button.is_clicked(event):
            self.running = False

    def handle_game_mode_input(self, event):
        """Handle button clicks in the game mode selection menu"""
        if self.pvp_button.is_clicked(event):
            self.vs_ai = False  # PvP mode
            self.state = 'color_selection'
        elif self.pve_button.is_clicked(event):
            self.vs_ai = True  # PvE mode (vs AI)
            self.state = 'color_selection'
        elif self.back_button.is_clicked(event):
            self.state = 'menu'

    def handle_color_selection_input(self, event):
        """Handle button clicks in the color selection menu"""
        if self.white_button.is_clicked(event):
            self.player_color = 'white'
            self.start_game()
        elif self.black_button.is_clicked(event):
            self.player_color = 'black'
            self.start_game()
        elif self.back_button.is_clicked(event):
            self.state = 'game_mode_menu'

    def start_game(self):
        """Initialize the engine and start the game"""
        self.engine = Engine(self.player_color, self.vs_ai)  # Pass the color and game mode to the engine
        self.state = 'game'
        self.engine.run()

    def run(self):
        """Main loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # Handle input based on the current state
                if self.state == 'menu':
                    self.handle_menu_input(event)
                elif self.state == 'game_mode_menu':
                    self.handle_game_mode_input(event)
                elif self.state == 'color_selection':
                    self.handle_color_selection_input(event)

            # Draw the current state
            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'game_mode_menu':
                self.draw_game_mode_menu()
            elif self.state == 'color_selection':
                self.draw_color_selection_menu()

            pygame.display.flip()


if __name__ == '__main__':
    main = Main()
    main.run()
