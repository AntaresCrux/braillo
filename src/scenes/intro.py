import pygame
from utils.settings import WIDTH, HEIGHT
from utils.colors import FADE_COLOR, BACKGROUND_COLOR
from utils.states import AppStates

class Intro:
    def __init__(self, assets):
        self.state = AppStates.FADE_IN
        self.assets = assets
        self.screen = pygame.display.get_surface()
        self.current_frame = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.fade_alpha = 255
        self.fade_speed = 5
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill(FADE_COLOR)

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        if self.state == AppStates.FADE_IN:
            self._update_fade_in()
        elif self.state == AppStates.GIF_PLAYBACK:
            self._update_gif_playback(current_time)
        elif self.state == AppStates.FADE_OUT:
            self._update_fade_out()

        if self.state == AppStates.MENU:
            return "menu"

    def draw(self):

        self.screen.fill(BACKGROUND_COLOR)

        if self.state in [AppStates.GIF_PLAYBACK, AppStates.FADE_OUT] and self.assets.gif_frames:
            self.screen.blit(self.assets.gif_frames[self.current_frame][0], self.assets.get_gif_position())
        
        if self.state in [AppStates.FADE_IN, AppStates.FADE_OUT]:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0))
        
        pygame.display.flip()

    def _update_fade_in(self):
        self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
        if self.fade_alpha == 0:
            self.state = AppStates.GIF_PLAYBACK
            self.last_frame_time = pygame.time.get_ticks()

    def _update_gif_playback(self, current_time):
        if self.assets.gif_frames:
            frame, delay = self.assets.gif_frames[self.current_frame]
            if current_time - self.last_frame_time > delay:
                self.current_frame = (self.current_frame + 1) % len(self.assets.gif_frames)
                self.last_frame_time = current_time
                if self.current_frame == 0:
                    self.state = AppStates.FADE_OUT

    def _update_fade_out(self):
        self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
        if self.fade_alpha == 255:
            print("Fade out completo, cambiando a menú")
            self.state = AppStates.MENU  # Cambiar al menú principal
