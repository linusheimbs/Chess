from settings import *


def draw_text_box(screen, text, position, font, size=36, padding=10, border_radius=10):
    """ Draws text with a background rectangle on the given screen """
    # Render the text surface
    text_surface = font.render(text, True, COLORS['text'])

    # Get the size of the text surface and calculate the background rect
    text_rect = text_surface.get_rect()
    bg_rect = text_rect.inflate(padding * 2, padding * 2)
    bg_rect.center = position

    # Draw the background rectangle with rounded corners
    pygame.draw.rect(screen, COLORS['button'], bg_rect, border_radius=border_radius)

    # Blit the text onto the screen, centered within the background rectangle
    text_rect.center = bg_rect.center
    screen.blit(text_surface, text_rect)
