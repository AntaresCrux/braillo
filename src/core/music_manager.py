# src/core/music_manager.py
import pygame

class MusicManager:
    def __init__(self, music_path):
        pygame.mixer.init()
        self.music_path = music_path
        self.is_playing_music = False
        self.volume = 0.5  # Volumen inicial

        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.set_volume(self.volume)

    def play_music(self):
        if not self.is_playing_music:
            pygame.mixer.music.play(-1)  #se mantiene tocando infinitamente
            self.is_playing_music = True

    def stop_music(self):
        if self.is_playing_music:
            pygame.mixer.music.stop()
            self.is_playing_music = False

    def set_volume(self, volume):
        self.volume = max(0.0, min(volume, 1.0))  # limite del volumen entre 0 y 1
        pygame.mixer.music.set_volume(self.volume)

    def get_volume(self):
        return self.volume

    def is_playing(self):
        return self.is_playing_music
    
    def refresh_status(self):
        if pygame.mixer.music.get_busy():
            self.is_playing_music = True
        else:
            self.is_playing_music = False


