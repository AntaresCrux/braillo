import pygame
import sys

class Letras:
    def __init__(self, image_path="assets/images/alfabeto.png", screen_width=400, screen_height=600, scroll_speed=10):
        pygame.init()

        self.IMAGE_PATH = image_path
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.SCROLL_SPEED = scroll_speed

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Alfabeto Braille Scrollable")

        try:
            self.image = pygame.image.load(self.IMAGE_PATH)
        except pygame.error as e:
            print(f"No se pudo cargar la imagen: {e}")
            sys.exit()

        self.image_rect = self.image.get_rect()
        self.scroll_y = 0
        self.is_dragging = False
        self.last_y = 0

        self.clock = pygame.time.Clock()
        self.running = True

    def ejecutar(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.is_dragging = True
                    self.last_y = event.pos[1]
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_dragging = False
                elif event.type == pygame.MOUSEMOTION and self.is_dragging:
                    dy = self.last_y - event.pos[1]
                    self.scroll_y += dy
                    self.last_y = event.pos[1]

            self.scroll_y = max(0, min(self.scroll_y, self.image_rect.height - self.SCREEN_HEIGHT))

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.image, (0, 0), area=pygame.Rect(0, self.scroll_y, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()