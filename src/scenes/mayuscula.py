import pygame
import random
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from ui.ui_helpers import draw_text_centered, draw_circle_with_label
from ui.sidebar_menu import SidebarMenu
from ui.popup_message import PopupMessage

class MayusculasScene:
    def __init__(self, assets, progress):
        self.assets = assets
        self.progress = progress
        self.screen = pygame.display.get_surface()

        self.ejercicios = [
            "Descubre el prefijo",
            "¿Minúscula o Mayúscula?",
            "Arma nombres propios",
            "Aplica en siglas"
        ]
        self.current_index = 0
        self.estado = "en_curso"
        self.popup = None

        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        self.sidebar = SidebarMenu(
            labels=["Descubre", "Clasifica", "Construye", "Siglas"],
            font=self.assets.fonts['default'],
            width=160,
            height=HEIGHT
        )

        self.puntos = [
            (180, 100), (180, 170), (180, 240),
            (300, 100), (300, 170), (300, 240)
        ]
        self.tocados = set()
        self.mostrar_feedback = ""

    def on_enter(self):
        self.reset_state()

    def handle_event(self, event):
        if self.popup:
            self.popup.handle_event(event)
            return

        if self.sidebar.visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_button_rect.collidepoint(event.pos):
                    self.sidebar.toggle()
                    return
                sidebar_index = self.sidebar.handle_event(event)
                if sidebar_index is not None:
                    self.switch_exercise(sidebar_index)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_button_rect.collidepoint(event.pos):
                self.sidebar.toggle()
                return
            if self.back_icon_rect.collidepoint(event.pos):
                return "select_level"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.next_exercise()
            elif event.key == pygame.K_LEFT:
                self.prev_exercise()

        if self.current_index == 0:
            self.handle_event_descubre(event)

    def handle_event_descubre(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (x, y) in enumerate(self.puntos):
                rect = pygame.Rect(x - 20, y - 20, 40, 40)
                if rect.collidepoint(event.pos):
                    self.tocados.add(i + 1)

            if {4, 6} == self.tocados:
                self.mostrar_modal_prefijo()
            elif len(self.tocados) > 2:
                self.mostrar_feedback = "Intenta de nuevo"
                self.tocados.clear()

    def mostrar_modal_prefijo(self):
        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['default'],
            title="¡Muy bien!",
            message="Los puntos 4 y 6 forman el prefijo de mayúscula en Braille.",
            on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "Descubre el prefijo"), self.next_exercise()),
            show_next=False
        )
        self.popup.show()
        self.estado = "completado"

    def update(self, dt):
        self.sidebar.update(dt)

    def draw(self):
        self.screen.fill((13, 59, 102))
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['big'], 30)

        if self.current_index == 0:
            self.draw_descubre()

        if self.sidebar.visible:
            sombra = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 100))
            self.screen.blit(sombra, (0, 0))
            self.sidebar.draw(self.screen)

        self.screen.blit(self.menu_icon, self.menu_button_rect.topleft)
        self.screen.blit(self.back_icon, self.back_icon_rect.topleft)

        if self.popup:
            self.popup.draw()

        pygame.display.flip()

    def draw_descubre(self):
        for i, (x, y) in enumerate(self.puntos):
            draw_circle_with_label(self.screen, (x, y), 30, str(i + 1), self.assets.fonts['default'])

        if self.mostrar_feedback:
            draw_text_centered(self.screen, self.mostrar_feedback, self.assets.fonts['default'], HEIGHT - 40, (255, 100, 100))

    def switch_exercise(self, index):
        self.current_index = index
        self.reset_state()

    def next_exercise(self):
        if self.current_index < len(self.ejercicios) - 1:
            self.current_index += 1
            self.reset_state()

    def prev_exercise(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.reset_state()

    def reset_state(self):
        self.estado = "en_curso"
        self.popup = None
        self.tocados.clear()
        self.mostrar_feedback = ""
