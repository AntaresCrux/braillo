import pygame
from ..core.assets_manager import AssetsManager
from ui.coverflow import CoverFlow
from utils.settings import AppStates, WIDTH, HEIGHT, BG_COLOR, FADE_COLOR, FPS

class BrailleApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Braille App")
        self.clock = pygame.time.Clock()
        self.assets = AssetsManager()
        self.coverflow = CoverFlow(self.assets.buttons)
        self.state = AppStates.FADE_IN
        self.current_frame = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.fade_alpha = 255
        self.fade_speed = 5
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill(FADE_COLOR)
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self._handle_events()
            self._update_state(dt)
            self._render()
        pygame.quit()
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.state == AppStates.INTERFACE:
                result = self.coverflow.handle_event(event)
                if result == len(self.assets.buttons) - 1:  # Último botón
                    return False
        return True
    
    def _update_state(self, dt):
        current_time = pygame.time.get_ticks()
        
        if self.state == AppStates.FADE_IN:
            self._update_fade_in(current_time)
        elif self.state == AppStates.GIF_PLAYBACK:
            self._update_gif_playback(current_time)
        elif self.state == AppStates.FADE_OUT:
            self._update_fade_out()
        elif self.state == AppStates.INTERFACE:
            self.coverflow.update(dt)
    
    def _render(self):
        self.screen.fill(BG_COLOR)
        
        if self.assets.background:
            self.screen.blit(self.assets.background, (0, 0))
        
        if self.state in [AppStates.GIF_PLAYBACK, AppStates.FADE_OUT] and self.assets.gif_frames:
            self.screen.blit(self.assets.gif_frames[self.current_frame][0], self.assets.get_gif_position())
        
        if self.state == AppStates.INTERFACE:
            self.coverflow.draw(self.screen)
        
        if self.state in [AppStates.FADE_IN, AppStates.FADE_OUT]:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0))
        
        pygame.display.flip()
    
    def _update_fade_in(self, current_time):
        """Reduce gradualmente la opacidad del fade-in hasta hacerlo desaparecer."""
        self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
        if self.fade_alpha == 0:
            self.state = AppStates.GIF_PLAYBACK
            self.last_frame_time = current_time

    def _update_gif_playback(self, current_time):
        """Muestra el GIF de introducción y cambia al siguiente estado al terminar."""
        if self.assets.gif_frames:
            frame, delay = self.assets.gif_frames[self.current_frame]
            if current_time - self.last_frame_time > delay:
                self.current_frame = (self.current_frame + 1) % len(self.assets.gif_frames)
                self.last_frame_time = current_time
                if self.current_frame == 0:
                    self.state = AppStates.FADE_OUT

    def _update_fade_out(self):
        """Incrementa la opacidad para el efecto de fade-out y cambia al estado final."""
        self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
        if self.fade_alpha == 255:
            self.state = AppStates.INTERFACE