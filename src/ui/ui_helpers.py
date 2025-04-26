import pygame

def draw_text_centered(surface, text, font, y, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    x = surface.get_width() // 2 - text_surface.get_width() // 2
    surface.blit(text_surface, (x, y))

def draw_shadowed_box(surface, rect, color, border_radius=20, shadow_color=(0, 0, 0, 100)):
    sombra = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    sombra.fill(shadow_color)
    surface.blit(sombra, rect.topleft)
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)

def draw_circle_with_label(surface, center, radius, label, font, color=(255, 255, 255), label_color=(255, 255, 255)):
    pygame.draw.circle(surface, color, center, radius)
    text = font.render(label, True, label_color)
    text_rect = text.get_rect(center=center)
    surface.blit(text, text_rect)

def draw_text_inside_rect(surface, text, font, rect, color=(0, 0, 0)):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)
