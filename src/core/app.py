import pygame
from core.assets_manager import AssetsManager
from core.progress_manager import ProgressManager
from core.state_manager import StateManager
from utils.settings import WIDTH, HEIGHT, FPS
from scenes.intro import Intro
from scenes.menu import Menu
from scenes.select_level import SelectLevel
from scenes.celda import CeldaScene
from scenes.numero import NumerosScene
from utils.settings import ASSETS_PATHS
from core.music_manager import MusicManager
from scenes.configurar import ConfigScene
from scenes.mayuscula import MayusculasScene


class BrailleApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Braille App")
        self.clock = pygame.time.Clock()
        self.assets = AssetsManager()
        self.progress = ProgressManager()
        self.state_manager = StateManager()
        self.music_manager = MusicManager(ASSETS_PATHS['music'])
        self.music_manager.play_music()
        self.state_manager.add_state("intro", Intro(self.assets))
        self.state_manager.add_state("menu", Menu(self.assets))
        self.state_manager.add_state("select_level", SelectLevel(self.assets, self.progress))
        self.state_manager.add_state("celdas", CeldaScene(self.assets, self.progress))
        self.state_manager.add_state("mayusculas", MayusculasScene(self.assets, self.progress))
        self.state_manager.add_state("numeros", NumerosScene(self.assets, self.progress))  # Cambiar a la escena de números
        self.state_manager.add_state("configurar", ConfigScene(self.assets, self.music_manager))
        self.state_manager.set_state("numeros") #para probar desde el principio

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self._handle_events()
            if running:
                self.state_manager.update(dt)
                self.state_manager.draw()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            result = self.state_manager.handle_event(event)

            if isinstance(result, str) and result in self.state_manager.states:
                self.state_manager.set_state(result)
                # Llama on_enter() si la escena tiene ese método
                state = self.state_manager.states[result]
                if hasattr(state, "on_enter"):
                    state.on_enter()

        return True
