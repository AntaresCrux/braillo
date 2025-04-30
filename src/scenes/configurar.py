import pygame
from utils.settings import ASSETS_PATHS
from utils.colors import BACKGROUND_COLOR, BLANCO, CREMA_CLARO, AMARILLO_PASTEL
from ui.ui_helpers import draw_text_centered
from ui.popup_message import PopupMessage

class ConfigScene:
    def __init__(self, assets, music_manager):
        self.assets = assets
        self.music_manager = music_manager
        self.screen = pygame.display.get_surface()

        # Botón regresar (izquierda)
        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_rect = self.back_icon.get_rect(topleft=(29, 240))

        # Botón info (centro)
        self.info_icon = pygame.image.load(ASSETS_PATHS['buttons']['info']).convert_alpha()
        self.info_icon = pygame.transform.smoothscale(self.info_icon, (60, 60))
        self.info_rect = self.info_icon.get_rect(topleft=(210, 240))

        # Música (derecha)
        self.music_on_icon = pygame.image.load(ASSETS_PATHS['buttons']['musica_on']).convert_alpha()
        self.music_off_icon = pygame.image.load(ASSETS_PATHS['buttons']['musica_off']).convert_alpha()
        self.music_on_icon = pygame.transform.smoothscale(self.music_on_icon, (60, 60))
        self.music_off_icon = pygame.transform.smoothscale(self.music_off_icon, (60, 60))
        self.music_icon_rect = self.music_on_icon.get_rect(topleft=(391, 240))
        self.music_enabled = self.music_manager.is_playing()

        # Slider de volumen (más abajo)
        self.volume = self.music_manager.get_volume()
        self.slider_rect = pygame.Rect(90, 170, 300, 10)
        self.slider_knob_rect = pygame.Rect(90 + int(self.volume * 300), 155, 40, 40)
        self.slider_knob_click_area = pygame.Rect(0, 0, 40, 40)
        self.slider_knob_click_area.center = self.slider_knob_rect.center
        self.dragging_knob = False

        #Mostrar popup de créditos
        self.popup = None


    def handle_event(self, event):
        if self.popup:
            result = self.popup.handle_event(event)
            if result == "close":
                self.popup = None
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_rect.collidepoint(event.pos):
                return "menu"

            if self.info_rect.collidepoint(event.pos):
                self.mostrar_creditos()

            if self.music_icon_rect.collidepoint(event.pos):
                self.music_enabled = not self.music_enabled
                if self.music_enabled:
                    self.music_manager.play_music()
                else:
                    self.music_manager.stop_music()

            if self.slider_knob_click_area.collidepoint(event.pos):
                self.dragging_knob = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_knob = False
            x = max(self.slider_rect.left, min(self.slider_knob_rect.centerx, self.slider_rect.right))
            self.slider_knob_rect.centerx = x
            self.slider_knob_click_area.centerx = x
            new_volume = (x - self.slider_rect.left) / 300
            self.music_manager.set_volume(new_volume)

        elif event.type == pygame.MOUSEMOTION and self.dragging_knob:
            x = max(self.slider_rect.left, min(event.pos[0], self.slider_rect.right))
            self.slider_knob_rect.centerx = x
            self.slider_knob_click_area.centerx = x
            new_volume = (x - self.slider_rect.left) / 300
            self.music_manager.set_volume(new_volume)

        return None


    def update(self, dt):
        pass


    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Título y subtítulo
        draw_text_centered(self.screen, "Configuraciones", self.assets.fonts['big'], y=30, color=BLANCO)
        draw_text_centered(self.screen, "Volumen", self.assets.fonts['default'], y=100, color=BLANCO)

        # Slider: barra base y parte rellena
        pygame.draw.rect(self.screen, CREMA_CLARO, self.slider_rect, border_radius=5)
        filled_width = self.slider_knob_rect.centerx - self.slider_rect.left
        if filled_width > 0:
            pygame.draw.rect(
                self.screen,
                AMARILLO_PASTEL,
                (self.slider_rect.left, self.slider_rect.top, filled_width, self.slider_rect.height),
                border_radius=5
            )

        # Perilla del slider (círculo)
        pygame.draw.circle(self.screen, AMARILLO_PASTEL, self.slider_knob_rect.center, 20)

        # Botones
        self.screen.blit(self.back_icon, self.back_rect.topleft)
        self.screen.blit(self.info_icon, self.info_rect.topleft)
        icon = self.music_on_icon if self.music_enabled else self.music_off_icon
        self.screen.blit(icon, self.music_icon_rect.topleft)

        #Popup de créditos
        if self.popup:
            self.popup.draw()

        pygame.display.flip()

    def mostrar_creditos(self):

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title="Créditos",
            message="A papá Dios",
            on_close=self.cerrar_popup,
            show_next=False
        )

        self.popup.show()

    def cerrar_popup(self):
        self.popup = None
