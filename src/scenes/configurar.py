import pygame
from utils.settings import HEIGHT, ASSETS_PATHS
from utils.colors import BACKGROUND_COLOR, BLANCO, CREMA_CLARO, AMARILLO_PASTEL, AZUL_OSCURO
from ui.ui_helpers import draw_text_centered

class ConfigScene:
    def __init__(self, assets, music_manager):
        self.assets = assets
        self.music_manager = music_manager
        self.screen = pygame.display.get_surface()

        # Botón regresar
        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        # Música
        self.music_on_icon = pygame.image.load(ASSETS_PATHS['buttons']['musica_on']).convert_alpha()
        self.music_off_icon = pygame.image.load(ASSETS_PATHS['buttons']['musica_off']).convert_alpha()
        self.music_on_icon = pygame.transform.smoothscale(self.music_on_icon, (60, 60))
        self.music_off_icon = pygame.transform.smoothscale(self.music_off_icon, (60, 60))
        self.music_icon_rect = self.music_on_icon.get_rect(topleft=(60, 100))
        self.music_enabled = self.music_manager.is_playing()

        # Slider de volumen
        self.volume = self.music_manager.get_volume()
        self.slider_rect = pygame.Rect(90, 180, 300, 10)
        self.slider_knob_rect = pygame.Rect(90 + int(self.volume * 300) - 5, 175, 10, 20)
        self.dragging_knob = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_rect.collidepoint(event.pos):
                return "menu"

            if self.music_icon_rect.collidepoint(event.pos):
                self.music_enabled = not self.music_enabled
                if self.music_enabled:
                    self.music_manager.play_music()
                else:
                    self.music_manager.stop_music()

            if self.slider_knob_rect.collidepoint(event.pos):
                self.dragging_knob = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_knob = False
            # Forzar ajuste del knob al soltar
            x = max(self.slider_rect.left, min(self.slider_knob_rect.centerx, self.slider_rect.right))
            self.slider_knob_rect.centerx = x
            new_volume = (x - self.slider_rect.left) / 300
            self.music_manager.set_volume(new_volume)

        elif event.type == pygame.MOUSEMOTION and self.dragging_knob:
            x = max(self.slider_rect.left, min(event.pos[0], self.slider_rect.right))
            self.slider_knob_rect.centerx = x
            new_volume = (x - self.slider_rect.left) / 300
            self.music_manager.set_volume(new_volume)

        return None

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)  # Color de la pantalla

        draw_text_centered(self.screen, "Configuraciones", self.assets.fonts['big'], 20, BLANCO)

        # Botón de regresar
        self.screen.blit(self.back_icon, self.back_rect.topleft)

        # Icono de música y texto
        icon = self.music_on_icon if self.music_enabled else self.music_off_icon
        self.screen.blit(icon, self.music_icon_rect.topleft)

        music_text = self.assets.fonts['default'].render("Música", True, BLANCO)
        self.screen.blit(music_text, (self.music_icon_rect.right + 10, self.music_icon_rect.y + 5))

        # Texto del volumen centrado
        volumen_text = self.assets.fonts['default'].render("Volumen", True, BLANCO)
        volumen_text_rect = volumen_text.get_rect(center=(self.slider_rect.centerx, self.slider_rect.top - 25))
        self.screen.blit(volumen_text, volumen_text_rect)

        # Barra de volumen
        pygame.draw.rect(self.screen, CREMA_CLARO, self.slider_rect, border_radius=5)  # Fondo crema clarito
        filled_width = self.slider_knob_rect.centerx - self.slider_rect.left
        if filled_width > 0:
            pygame.draw.rect(self.screen, AMARILLO_PASTEL, (self.slider_rect.left, self.slider_rect.top, filled_width, self.slider_rect.height), border_radius=5)

        # Circulito para mover el volumen
        pygame.draw.circle(self.screen, AMARILLO_PASTEL, self.slider_knob_rect.center, 20)
        pygame.draw.circle(self.screen, CREMA_CLARO, self.slider_knob_rect.center, 30, 2)  # Contorno 

        pygame.display.flip()
