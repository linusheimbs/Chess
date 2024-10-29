from settings import *


class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font

    def draw(self, surface):
        """ Draw the button with hover effect """
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = COLORS['button_hover'] if is_hovered else COLORS['button']

        # Draw the button background (with rounded corners if you like)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        # Render the text
        text_surface = self.font.render(self.text, True, COLORS['text'])
        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

    def is_clicked(self, event):
        """ Check if the button is clicked """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
