import pygame
from utils.settings import WIDTH, HEIGHT
from utils.estructura_basico import estructura_basico

class SelectLevel:
    def __init__(self, assets, progress):
        self.assets = assets 
        self.progress = progress
        self.screen = pygame.display.get_surface()

        # Fondo largo
        self.bg = self.assets.images['world_map']
        self.bg_width = self.bg.get_width()

        # Scroll horizontal
        self.scroll_x = 0
        self.dragging = False
        self.drag_start_x = 0

        # Botón de regresar
        self.back_img = self.assets.buttons['back'][0]
        self.back_rect = self.back_img.get_rect(topleft=(18, 240))

        # Nodos del nivel básico (pos x, y, id único)
        self.nodos = [
            (100, 180, "celdas"),
            (350, 120, "alfabeto"),
            (600, 200, "mayusculas"),
            (850, 140, "numeros"),
            (1100, 210, "signos"),
            (1350, 130, "desfinal")
        ]

        self.completed_levels = self._detectar_niveles_completos()

    def _detectar_niveles_completos(self):
        completados = set()
        niveles = [n[2] for n in self.nodos]
        for nivel_id in niveles:
            if self.progress.is_nivel_completo(nivel_id, estructura_basico):
                completados.add(nivel_id)
        return completados

    def _is_unlocked(self, level_id):
        if level_id == "celdas":
            return True  # Siempre desbloqueado al inicio

        ids = [n[2] for n in self.nodos]
        index = ids.index(level_id)
        if index == 0:
            return True

        anterior_id = ids[index - 1]
        return self.progress.is_nivel_completo(anterior_id, estructura_basico)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_rect.collidepoint(event.pos):
                return "menu"
            self.dragging = True
            self.drag_start_x = event.pos[0]

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.drag_start_x
            if abs(dx) > 2:
                self.scroll_x -= dx
                self.scroll_x = max(0, min(self.scroll_x, self.bg_width - WIDTH))
                self.drag_start_x = event.pos[0]

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            x_mouse = event.pos[0] + self.scroll_x
            y_mouse = event.pos[1]

            for x, y, level_id in self.nodos:
                if not self._is_unlocked(level_id):
                    continue  # Ignorar nodos bloqueados
                rect = pygame.Rect(x, y, 100, 100)
                if rect.collidepoint(x_mouse, y_mouse):
                    return level_id # Celdas

        return None

    def update(self, dt):
        self.completed_levels = self._detectar_niveles_completos()

    def draw(self):
        # Dibujar fondo con scroll
        viewport = pygame.Rect(self.scroll_x, 0, WIDTH, HEIGHT)
        self.screen.blit(self.bg, (0, 0), viewport)

        # Dibujar nodos con desplazamiento y aplicar sombra si están bloqueados
        for x, y, level_id in self.nodos:
            key = f"{level_id}_on"
            img = self.assets.images.get(key)
            if img:
                pos = (x - self.scroll_x, y)
                self.screen.blit(img, pos)
                if not self._is_unlocked(level_id):
                    w, h = img.get_size()
                    sombra = pygame.Surface((w, h), pygame.SRCALPHA)
                    pygame.draw.rect(sombra, (0, 0, 0, 120), (0, 0, w, h), border_radius=10)
                    self.screen.blit(sombra, pos)

        # Botón de regreso
        self.screen.blit(self.back_img, self.back_rect)
        pygame.display.flip()
