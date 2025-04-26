import pygame
import json
import random
from pathlib import Path
from utils.settings import WIDTH, HEIGHT
from utils.colors import BG_COLOR

DATA_PATH = Path("assets/data/braille_letters.json")

class Gameplay:
    def __init__(self, assets):
        self.assets = assets
        #self.level_id = level_id
        self.screen = pygame.display.get_surface()
        self.font = self.assets.fonts['big']
        self.small_font = self.assets.fonts['default']

        self.letters_data = self._load_letters()
        self.current_letter = None
        self.correct_points = []
        self.selected_points = []

        self.braille_buttons = self._create_braille_buttons()
        self.validate_button = pygame.Rect(WIDTH - 130, HEIGHT - 60, 100, 40)

        self.feedback = ""
        self.next_letter()

    def _load_letters(self):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def next_letter(self):
        self.current_letter = random.choice(list(self.letters_data.keys()))
        self.correct_points = self.letters_data[self.current_letter]
        self.selected_points = []
        self.feedback = ""

    def _create_braille_buttons(self):
        buttons = []
        start_x = WIDTH // 2 - 50
        start_y = HEIGHT // 2 - 90
        spacing_x = 60
        spacing_y = 60

        # Orden Braille: 1 4, 2 5, 3 6
        positions = [
            (0, 0),  # Punto 1
            (0, 1),  # Punto 2
            (0, 2),  # Punto 3
            (1, 0),  # Punto 4
            (1, 1),  # Punto 5
            (1, 2)   # Punto 6
        ]

        for i, (col, row) in enumerate(positions):
            x = start_x + col * 60
            y = start_y + row * spacing_y
            buttons.append({
                'rect': pygame.Rect(x, y, 40, 40),
                'active': False,
                'point_id': i + 1
            })
        """
        for i in range(6):
            col = i % 2
            row = i // 2
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            buttons.append({
                'rect': pygame.Rect(x, y, 40, 40),
                'active': False,
                'point_id': i + 1
            })
        """    
        return buttons

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            print(f"🖱️ Clic detectado en: {pos}")  # DEBUG

            for btn in self.braille_buttons:
                if btn['rect'].collidepoint(pos):
                    btn['active'] = not btn['active']
                    print(f"🎯 Botón {btn['point_id']} activado: {btn['active']}")  # DEBUG

            if self.validate_button.collidepoint(pos):
                print("✅ Validar presionado")  # DEBUG
                self._validate_answer()

    def _validate_answer(self):
        self.selected_points = [btn['point_id'] for btn in self.braille_buttons if btn['active']]
        if sorted(self.selected_points) == sorted(self.correct_points):
            self.feedback = "¡Correcto!"
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Espera antes de cambiar
        else:
            self.feedback = "Intenta de nuevo"

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Mostrar letra actual
        text = self.font.render(self.current_letter, True, (0, 0, 0))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 40))

        # Dibujar botones de Braille
        for btn in self.braille_buttons:
            color = (50, 200, 50) if btn['active'] else (200, 200, 200)
            pygame.draw.circle(self.screen, color, btn['rect'].center, 20)
            pygame.draw.circle(self.screen, (0, 0, 0), btn['rect'].center, 20, 2)

        # Botón validar
        pygame.draw.rect(self.screen, (0, 150, 255), self.validate_button, border_radius=10)
        label = self.small_font.render("Validar", True, (255, 255, 255))
        self.screen.blit(label, (
            self.validate_button.centerx - label.get_width() // 2,
            self.validate_button.centery - label.get_height() // 2))

        # Feedback
        if self.feedback:
            msg = self.small_font.render(self.feedback, True, (0, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()

    def handle_custom_event(self, event):
        if event.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            self.next_letter()
