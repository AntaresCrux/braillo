import pygame
from utils.settings import WIDTH, HEIGHT
from ui.ui_helpers import draw_text_inside_rect

class SidebarMenu:
    def __init__(self, labels, font, width=160, height=HEIGHT):
        self.labels = labels
        self.font = font
        self.width = width
        self.height = height
        self.visible = False
        self.rect = pygame.Rect(WIDTH - self.width, 0, self.width, self.height)

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event):
        if not self.visible:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                for i, _ in enumerate(self.labels):
                    btn_rect = pygame.Rect(self.rect.x + 10, 60 + i * 60, self.width - 20, 45)
                    if btn_rect.collidepoint(event.pos):
                        return i
        return None

    def update(self, dt):
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, (252, 244, 220), self.rect, border_radius=30)

        for i, label in enumerate(self.labels):
            btn_rect = pygame.Rect(self.rect.x + 10, 60 + i * 60, self.width - 20, 45)
            pygame.draw.rect(surface, (251, 211, 78), btn_rect, border_radius=20)
            draw_text_inside_rect(surface, label, self.font, btn_rect, (13, 59, 102))
