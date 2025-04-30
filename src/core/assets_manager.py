import pygame
from PIL import Image, ImageSequence
from pathlib import Path
from utils.settings import ASSETS_PATHS, WIDTH, HEIGHT
from utils.settings import load_fonts

class AssetsManager:
    def __init__(self):
        self.buttons = {}
        self.gif_frames = []
        self.gif_size = (0, 0)
        self.fonts = {}
        self.images = {}
        self.fichas = {}
        self.load_assets()

    def load_assets(self):
        self._load_buttons()
        self._load_gif()
        self._load_fonts()
        self._load_images()
        self._load_fichas()

    def _load_images(self):
        for name, path in ASSETS_PATHS.get('images', {}).items():
            try:
                img = pygame.image.load(path).convert_alpha()
                if name.startswith("nodo"):
                    img = pygame.transform.smoothscale(img, (100, 195.47))
                self.images[name] = img
            except Exception as e:
                print(f"Error loading image '{name}': {e}")

    def _load_fonts(self):
        try:
            self.fonts = load_fonts()
        except Exception as e:
            print(f"Error loading fonts: {e}")

    def _load_gif(self):
        try:
            gif = Image.open(ASSETS_PATHS['gif'])
            frames = []
            original_size = gif.size
            ratio = min(WIDTH / original_size[0], HEIGHT / original_size[1])
            self.gif_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))

            for frame in ImageSequence.Iterator(gif):
                duration = frame.info.get('duration', 100)
                frame = frame.convert("RGBA").resize(self.gif_size, Image.LANCZOS)
                pygame_frame = pygame.image.fromstring(frame.tobytes(), self.gif_size, "RGBA")
                frames.append((pygame_frame, max(10, duration)))

            self.gif_frames = frames
        except Exception as e:
            print(f"Error loading GIF: {e}")

    def _load_buttons(self):
        for name, path in ASSETS_PATHS['buttons'].items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self.buttons[name] = (img, name.capitalize())
            except Exception as e:
                print(f"Error loading button: {path} ({e})")
                self.buttons[name] = self._create_fallback_button(name)

    def _create_fallback_button(self, name):
        surf = pygame.Surface((96, 96), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 107, 53), (0, 0, 96, 96), border_radius=15)
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(name.title(), True, (255, 255, 255))
        surf.blit(text, (48 - text.get_width() // 2, 48 - text.get_height() // 2))
        return (surf, name.capitalize())

    def get_gif_position(self):
        return ((WIDTH - self.gif_size[0]) // 2, (HEIGHT - self.gif_size[1]) // 2) if self.gif_size else (0, 0)

    def _load_fichas(self):
        # Cargamos el prefijo
        try:
            self.fichas["prefijo"] = pygame.image.load(ASSETS_PATHS['fichas']['prefijo']).convert_alpha()
        except Exception as e:
            print(f"Error loading ficha prefijo: {e}")

        # Cargamos los números
        for num, path in ASSETS_PATHS['fichas']['numeros'].items():
            try:
                self.fichas[num] = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Error loading ficha numero {num}: {e}")

        # Cargar separadores de numeros (decimal/miles)
        for sep, path in ASSETS_PATHS['fichas']['separadores'].items():
            try:
                if sep == "miles":
                    self.fichas[","] = pygame.image.load(path).convert_alpha()
                elif sep == "decimal":
                    self.fichas["."] = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Error loading ficha separador {sep}: {e}")
