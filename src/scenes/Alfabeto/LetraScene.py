# src/scenes/Alfabeto/LetraScene.py
import pygame
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BLANCO
from ui.sidebar_menu import SidebarMenu
from scenes.Alfabeto.escribe import EscribeLetra
from scenes.Alfabeto.identifica import IdentificaLetra
from scenes.Alfabeto.acomoda import AcomodaLetra

class LetraScene:
    def __init__(self, assets, progress):
        self.assets = assets
        self.progress = progress
        self.screen = pygame.display.get_surface()

        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.back_icon_rect = pygame.Rect(10, HEIGHT - 70, 60, 60)
        

        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))

        self.sidebar = SidebarMenu(
            labels=["Escribe", "Identifica", "Acomoda"],
            font=self.assets.fonts['small'],
            width=240,
            height=HEIGHT
        )

        # Cargar JSON de letras
        self.braille_map = self.cargar_braille_letras("assets/data/braille_letters.json")

        # Inicializar minijuegos
        self.minijuegos = {
            "escribe": EscribeLetra(self.assets, self.braille_map, self.avanzar_a_identifica),
            "identifica": IdentificaLetra(self.assets, self.braille_map, self.avanzar_a_acomoda),
            "acomoda": AcomodaLetra(self.assets, "assets/data/braille_letters.json", self.terminar_actividad)
        }

        self.modo_actual = "escribe"
        self.popup = None

    def cargar_braille_letras(self, path):
        import json
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["letras"]

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "exit"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.menu_button_rect.collidepoint(event.pos):
                self.sidebar.toggle()
                return
            if self.back_icon_rect.collidepoint(event.pos):
                return "select_level"

        if self.sidebar.visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                index = self.sidebar.handle_event(event)
                if index is not None:
                    modo = ["escribe", "identifica", "acomoda"][index]
                    self.modo_actual = modo
                    self.minijuegos[modo].__init__(self.assets, self.braille_map if modo != "acomoda" else "assets/data/braille_letters.json", self._get_callback(modo))
            return

        self.minijuegos[self.modo_actual].handle_event(event)

    def update(self, dt):
        self.sidebar.update(dt)
        self.minijuegos[self.modo_actual].update(dt)

    def draw(self):
        self.screen.fill((13, 59, 102))

        from ui.ui_helpers import draw_text_centered
        draw_text_centered(self.screen, self.modo_actual.capitalize() + " la letra", self.assets.fonts['default'], 30, color=BLANCO)

        self.minijuegos[self.modo_actual].draw(self.screen)

        # Menú lateral
        if self.sidebar.visible:
            sombra = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 100))
            self.screen.blit(sombra, (0, 0))
            self.sidebar.draw(self.screen)

        self.screen.blit(self.menu_icon, self.menu_button_rect.topleft)
        self.screen.blit(self.back_icon, self.back_icon_rect.topleft)

        pygame.display.flip()

    # === Callbacks de transición ===
    def avanzar_a_identifica(self):
        self.modo_actual = "identifica"

    def avanzar_a_acomoda(self):
        self.modo_actual = "acomoda"

    def terminar_actividad(self):
        return "menu"

    def _get_callback(self, modo):
        return {
            "escribe": self.avanzar_a_identifica,
            "identifica": self.avanzar_a_acomoda,
            "acomoda": self.terminar_actividad
        }[modo]


if __name__ == "__main__":
    from src.core.assets_manager import AssetsManager
    from src.core.progress_manager import ProgressManager

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    assets = AssetsManager()
    progress = ProgressManager()
    scene = LetraScene(assets, progress)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(30)
        for event in pygame.event.get():
            result = scene.handle_event(event)
            if result == "select_level" or result == "exit" or result == "menu":
                running = False

        scene.update(dt)
        scene.draw()

    pygame.quit()