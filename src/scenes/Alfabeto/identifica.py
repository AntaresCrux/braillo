# src/scenes/Alfabeto/identifica.py
import pygame
import random
from ui.popup_message import PopupMessage
from utils.settings import WIDTH, HEIGHT

class IdentificaLetra:
    def __init__(self, assets, braille_map, on_completo_callback):
        self.assets = assets
        self.braille_map = braille_map
        self.on_completo_callback = on_completo_callback

        self.intentos = 0
        self.max_intentos = 3
        self.popup = None

        self.drop_target_rect = pygame.Rect(WIDTH - 160, HEIGHT // 2 - 85, 120, 120)
        self.resultado_color = None
        self.drop_ficha_activa = None
        self.reset_drop_timer = None

        self.iniciar_nuevo()

    def iniciar_nuevo(self):
        self.objetivo_letra = random.choice(list(self.braille_map.keys()))
        self.opciones_fichas = [self.objetivo_letra]
        otras = list(self.braille_map.keys())
        otras.remove(self.objetivo_letra)
        self.opciones_fichas += random.sample(otras, 4)
        random.shuffle(self.opciones_fichas)

        self.ficha_imagenes = {
            letra: pygame.image.load(f"assets/images/{letra.lower()}.png").convert_alpha()
            for letra in self.opciones_fichas
        }

        ficha_y = HEIGHT - 100
        self.ficha_posiciones = {}
        for i, letra in enumerate(self.opciones_fichas):
            x = 80 + i * 75
            self.ficha_posiciones[letra] = {"pos": [x, ficha_y], "dragging": False, "offset": (0, 0)}

        self.resultado_color = None
        self.drop_ficha_activa = None
        self.reset_drop_timer = None

    def handle_event(self, event):
        if self.popup:
            self.popup.handle_event(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            for letra, ficha in self.ficha_posiciones.items():
                rect = pygame.Rect(ficha["pos"][0], ficha["pos"][1], 80, 80)
                if rect.collidepoint(event.pos):
                    ficha["dragging"] = True
                    offset_x = event.pos[0] - ficha["pos"][0]
                    offset_y = event.pos[1] - ficha["pos"][1]
                    ficha["offset"] = (offset_x, offset_y)

        elif event.type == pygame.MOUSEMOTION:
            for ficha in self.ficha_posiciones.values():
                if ficha["dragging"]:
                    mx, my = event.pos
                    ox, oy = ficha["offset"]
                    ficha["pos"][0] = mx - ox
                    ficha["pos"][1] = my - oy

        elif event.type == pygame.MOUSEBUTTONUP:
            for letra, ficha in self.ficha_posiciones.items():
                if ficha["dragging"]:
                    ficha["dragging"] = False
                    rect = pygame.Rect(ficha["pos"][0], ficha["pos"][1], 80, 80)
                    if self.drop_target_rect.colliderect(rect):
                        self.drop_ficha_activa = letra
                        if letra == self.objetivo_letra:
                            self.resultado_color = (0, 200, 0)
                        else:
                            self.resultado_color = (200, 0, 0)
                        self.reset_drop_timer = pygame.time.get_ticks() + 1000

    def update(self, dt):
        if self.reset_drop_timer and pygame.time.get_ticks() >= self.reset_drop_timer:
            self.reset_drop_timer = None

            if self.drop_ficha_activa == self.objetivo_letra:
                self.mostrar_popup("¡Correcto! Era la letra " + self.objetivo_letra)
            else:
                # Regresar ficha
                idx = self.opciones_fichas.index(self.drop_ficha_activa)
                self.ficha_posiciones[self.drop_ficha_activa]["pos"] = [80 + idx * 75, HEIGHT - 100]
                self.resultado_color = None
                self.drop_ficha_activa = None

    def mostrar_popup(self, mensaje):
        self.popup = PopupMessage(
            pygame.display.get_surface(),
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title="RESULTADO",
            message=mensaje,
            on_close=self.continuar,
            on_next=None,
            show_next=False
        )
        self.popup.show()

    def continuar(self):
        self.popup = None
        self.intentos += 1
        if self.intentos >= self.max_intentos:
            self.on_completo_callback()
        else:
            self.iniciar_nuevo()

    def draw(self, screen):
        sombra = self.assets.fonts['big'].render(self.objetivo_letra, True, (0, 0, 0))
        texto = self.assets.fonts['big'].render(self.objetivo_letra, True, (255, 255, 255))
        centro_y = HEIGHT // 2 - 40
        screen.blit(sombra, (82, centro_y - sombra.get_height() // 2 + 2))
        screen.blit(texto, (80, centro_y - texto.get_height() // 2))

        pygame.draw.rect(screen, self.resultado_color if self.resultado_color else (200, 200, 200),
                         self.drop_target_rect, border_radius=12)

        for letra, ficha in self.ficha_posiciones.items():
            ficha_img = pygame.transform.scale(self.ficha_imagenes[letra], (55, 65))
            screen.blit(ficha_img, ficha["pos"])

        if self.popup:
            self.popup.draw()