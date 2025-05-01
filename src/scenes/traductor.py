import pygame
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BACKGROUND_COLOR, AMARILLO_PASTEL, NARANJA, CREMA_CLARO, ROJO_ANARANJADO, NEGRO
from ui.ui_helpers import draw_text_centered

class TraductorScene:
    def __init__(self, assets):
        self.assets = assets
        self.screen = pygame.display.get_surface()

        self.texto = ""
        self.texto_traducido = ""
        self.texto_activo = False
        self.input_rect = pygame.Rect(40, 80, 400, 60)
        self.braille_rect = pygame.Rect(40, 150, 400, 90)

        self.scroll_x = 0
        self.scroll_input_x = 0
        self.dragging = False
        self.drag_start_x = 0
        self.max_scroll = 0
        self.max_scroll_input = 0

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        self.check_icon = pygame.image.load(ASSETS_PATHS['buttons']['traducir']).convert_alpha()
        self.check_icon_rect = self.check_icon.get_rect(bottomleft=(380, 70))

        self.clean_icon = pygame.image.load(ASSETS_PATHS['buttons']['limpiar']).convert_alpha()
        self.clean_icon_rect = self.clean_icon.get_rect(bottomleft=(380, 300))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.texto_activo = True
                self.dragging = True
                self.drag_start_x = event.pos[0]
            elif self.braille_rect.collidepoint(event.pos):
                self.texto_activo = False
                self.dragging = True
                self.drag_start_x = event.pos[0]
            else:
                self.texto_activo = False

            if self.back_icon_rect.collidepoint(event.pos):
                self.texto = ""
                self.texto_traducido = ""
                return "select_level"
            elif self.clean_icon_rect.collidepoint(event.pos):
                self.texto = ""
                self.texto_traducido = ""
                self.scroll_x = 0
                self.scroll_input_x = 0
            elif self.check_icon_rect.collidepoint(event.pos):
                self.texto_traducido = self.texto_a_braille(self.texto)
                self.scroll_x = 0

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.drag_start_x
                self.drag_start_x = event.pos[0]
                if self.texto_activo:
                    self.scroll_input_x += dx
                    self.scroll_input_x = max(min(self.scroll_input_x, 0), -self.max_scroll_input)
                else:
                    self.scroll_x += dx
                    self.scroll_x = max(min(self.scroll_x, 0), -self.max_scroll)

        elif event.type == pygame.KEYDOWN and self.texto_activo:
            if event.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif len(self.texto) < 100:
                self.texto += event.unicode

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        draw_text_centered(self.screen, "Traductor", self.assets.fonts['default'], y=30, color=AMARILLO_PASTEL)

        # Render del texto de entrada con clipping
        input_surface = pygame.Surface((self.input_rect.width, self.input_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(input_surface, CREMA_CLARO, input_surface.get_rect(), border_radius=8)  # fondo
        pygame.draw.rect(input_surface, NEGRO, input_surface.get_rect(), 4, border_radius=8)   # borde

        texto_surface = self.assets.fonts['big'].render(self.texto, True, NEGRO)
        texto_width = texto_surface.get_width()
        self.max_scroll_input = max(0, texto_width - self.input_rect.width + 20)

        input_surface.blit(texto_surface, (10 + self.scroll_input_x, 10))
        self.screen.blit(input_surface, self.input_rect.topleft)

        # Render del texto Braille con clipping
        pygame.draw.rect(self.screen, CREMA_CLARO, self.braille_rect, border_radius=8)
        pygame.draw.rect(self.screen, ROJO_ANARANJADO, self.braille_rect, 4, border_radius=8)

        braille_surface = pygame.Surface((self.braille_rect.width, self.braille_rect.height), pygame.SRCALPHA)
        braille_render = self.assets.fonts['braille_huge_2'].render(self.texto_traducido, True, ROJO_ANARANJADO)
        braille_width = braille_render.get_width()
        self.max_scroll = max(0, braille_width - self.braille_rect.width + 20)

        braille_surface.blit(braille_render, (self.scroll_x + 10, 10))
        self.screen.blit(braille_surface, self.braille_rect.topleft)

        self.screen.blit(self.back_icon, self.back_icon_rect.topleft)
        self.screen.blit(self.check_icon, self.check_icon_rect.topleft)
        self.screen.blit(self.clean_icon, self.clean_icon_rect.topleft)

        pygame.display.flip()

    def texto_a_braille(self, texto):
        mayus_prefix = '\u2828'  # ⠨
        num_prefix = '\u283C'    # ⠼

        numero_map = {
            '1': '\u2801', '2': '\u2803', '3': '\u2809', '4': '\u2819', '5': '\u2811',
            '6': '\u280B', '7': '\u281B', '8': '\u2813', '9': '\u280A', '0': '\u281A'
        }

        resultado = []
        en_numeros = False

        for c in texto:
            if c.isdigit():
                if not en_numeros:
                    resultado.append(num_prefix)
                    en_numeros = True
                resultado.append(numero_map.get(c, '?'))
            else:
                en_numeros = False
                if c.isalpha() and c.isupper():
                    resultado.append(mayus_prefix)
                    resultado.append(c.lower())
                else:
                    resultado.append(c)

        return ''.join(resultado)
