import pygame
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from ui.ui_helpers import draw_text_inside_rect

class SidebarMenu:
    def __init__(self, labels, font, width=240, height=HEIGHT):
        self.labels = labels
        self.font = font
        self.width = width
        self.height = height
        self.visible = False                                                    # Estado lógico se muestra o no
        self.current_x = WIDTH                                                  # Inicia oculto, fuera de la pantalla
        self.target_x = WIDTH                                                   # Posición objetivo
        self.rect = pygame.Rect(self.current_x, 0, self.width, self.height)

        # Configuración de botones dentro del menu
        self.button_width = 200
        self.button_height = 42
        self.button_spacing = 18

        # Velocidad de despliegue
        self.speed = 800  

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.target_x = WIDTH - self.width  # Lo mostramos
        else:
            self.target_x = WIDTH               # Lo ocultamos

    def handle_event(self, event):
        if self.current_x != WIDTH - self.width:
            return None  #No deja clickear hasta que esté desplegado

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                button_area_height = len(self.labels) * self.button_height + (len(self.labels) - 1) * self.button_spacing
                start_y = (self.height - button_area_height) // 2

                for i, _ in enumerate(self.labels):
                    btn_rect = pygame.Rect(
                        self.rect.x + (self.width - self.button_width) // 2,
                        start_y + i * (self.button_height + self.button_spacing),
                        self.button_width,
                        self.button_height
                    )
                    if btn_rect.collidepoint(event.pos):
                        return i
        return None

    def update(self, dt):
        # Le dice haci donde se va animar, que dirección
        if self.current_x < self.target_x:
            self.current_x += self.speed * dt
            if self.current_x > self.target_x:
                self.current_x = self.target_x
        elif self.current_x > self.target_x:
            self.current_x -= self.speed * dt
            if self.current_x < self.target_x:
                self.current_x = self.target_x

        #Confirmacion, al estar completamente oculto, ya no está visible
        if self.current_x >= WIDTH:
            self.visible = False

        self.rect.x = int(self.current_x)


    def draw(self, surface):
        # Si ya esta oculto y no es visible, no se dibuja dibujar
        if not self.visible and self.current_x >= WIDTH:
            return

        # Fondo del menu
        pygame.draw.rect(surface, (252, 244, 220), self.rect, border_radius=20)

        # Botones
        button_area_height = len(self.labels) * self.button_height + (len(self.labels) - 1) * self.button_spacing
        start_y = (self.height - button_area_height) // 2

        for i, label in enumerate(self.labels):
            btn_rect = pygame.Rect(
                self.rect.x + (self.width - self.button_width) // 2,
                start_y + i * (self.button_height + self.button_spacing),
                self.button_width,
                self.button_height
            )
            pygame.draw.rect(surface, (251, 211, 78), btn_rect, border_radius=20)
            draw_text_inside_rect(surface, label, self.font, btn_rect, (13, 59, 102))

