import pygame
from utils.settings import WIDTH, HEIGHT
from ui.sidebar_menu import SidebarMenu
from ui.popup_message import PopupMessage
from ui.ui_helpers import draw_text_centered, draw_circle_with_label

class BaseBrailleScene:
    def __init__(self, assets, progress, nivel_id, ejercicios, sidebar_labels):
        self.assets = assets
        self.progress = progress
        self.nivel_id = nivel_id  # Ej: "basico_1"
        self.screen = pygame.display.get_surface()
        self.ejercicios = ejercicios  # Lista de nombres
        self.current_index = 0
        self.estado = "en_curso"
        self.popup = None

        self.sidebar = SidebarMenu(labels=sidebar_labels, font=self.assets.fonts['default'], width=160, height=HEIGHT)

        self.menu_icon = self._load_icon('menu', (60, 60))
        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)

        self.back_icon = self._load_icon('back', (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

    def _load_icon(self, key, size):
        icon = pygame.image.load(self.assets.buttons[key][0]).convert_alpha()
        return pygame.transform.smoothscale(icon, size)

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

        # Redirige evento al método correspondiente
        getattr(self, f"handle_event_{self.current_index}", lambda e: None)(event)

    def update(self, dt):
        self.sidebar.update(dt)

    def draw(self):
        self.screen.fill((13, 59, 102))
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['big'], 30)

        getattr(self, f"draw_{self.current_index}", lambda: None)()

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

    def mostrar_popup(self, seccion, ejercicio, mensaje="Ejercicio completado", seccion_completa=False):
        ya_completado = ejercicio in self.progress.get_completed(self.nivel_id, seccion)
        self.progress.mark_exercise_done(self.nivel_id, seccion, ejercicio)
        self.estado = "completado"

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['default'],
            title="¡Buen repaso!" if ya_completado else "¡Felicidades!",
            message=mensaje,
            on_close=lambda: setattr(self, "popup", None),
            on_next=None if seccion_completa else self.next_exercise,
            show_next=not seccion_completa
        )
        self.popup.show()

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
        # Agrega aquí limpieza específica de cada ejercicio si es necesario
