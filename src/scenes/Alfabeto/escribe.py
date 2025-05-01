# src/scenes/Alfabeto/escribe.py
import pygame
import random
from ui.ui_helpers import draw_circle_with_label
from ui.popup_message import PopupMessage
from utils.settings import WIDTH, HEIGHT

class EscribeLetra:
    def __init__(self, assets, braille_map, on_completo_callback):
        self.assets = assets
        self.braille_map = braille_map
        self.on_completo_callback = on_completo_callback

        self.puntos = [
            (WIDTH - 145, 120), (WIDTH - 145, 180), (WIDTH - 145, 241),
            (WIDTH - 74, 120),  (WIDTH - 74, 180),  (WIDTH - 74, 241)
        ]

        self.objetivo_letra = ""
        self.objetivo_puntos = []
        self.seleccion_usuario = {}

        self.ficha_base = pygame.image.load("assets/images/FichaBase.png").convert_alpha()
        self.ficha_base = pygame.transform.scale(self.ficha_base, (160, 230))  # ajusta tamaño si necesario

        self.aciertos = 0
        self.inactividad_timeout = 5000
        self.last_touch_time = pygame.time.get_ticks()
        self.inactividad_detectada = False
        self.evaluar_button = pygame.Rect(130, 250, 150, 40)
        self.popup = None

        self.generar_letra()

    def generar_letra(self):
        self.objetivo_letra = random.choice(list(self.braille_map.keys()))
        self.objetivo_puntos = self.braille_map[self.objetivo_letra]
        self.seleccion_usuario.clear()
        self.last_touch_time = pygame.time.get_ticks()
        self.inactividad_detectada = False

    def handle_event(self, event):
        if self.popup:
            self.popup.handle_event(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.last_touch_time = pygame.time.get_ticks()
            self.inactividad_detectada = False

            if self.evaluar_button.collidepoint(event.pos):
                self.inactividad_detectada = True
                self.evaluar_usuario()
                return

            for i, (x, y) in enumerate(self.puntos):
                if pygame.Rect(x - 20, y - 20, 40, 40).collidepoint(event.pos):
                    punto = i + 1
                    if punto in self.seleccion_usuario:
                        del self.seleccion_usuario[punto]
                    else:
                        correcto = punto in self.objetivo_puntos
                        self.seleccion_usuario[punto] = "correcto" if correcto else "incorrecto"

    def update(self, dt):
        if not self.popup and not self.inactividad_detectada:
            if pygame.time.get_ticks() - self.last_touch_time >= self.inactividad_timeout:
                self.inactividad_detectada = True
                self.evaluar_usuario()

    def evaluar_usuario(self):
        seleccionados = set(self.seleccion_usuario.keys())
        correctos = set(self.objetivo_puntos)

        if seleccionados == correctos:
            mensaje = "¡Correcto! Has escrito bien la letra."
            self.aciertos += 1
        else:
            mensaje = "Incorrecto. Intenta de nuevo."

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
        if self.aciertos >= 3:
            self.on_completo_callback()
        else:
            self.generar_letra()

    def draw(self, screen):
        screen.fill((13, 59, 102))
        titulo = self.assets.fonts['default'].render("Escribe la letra", True, (255, 255, 255))
        screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 20))

        letra_surface = self.assets.fonts['big'].render(self.objetivo_letra, True, (255, 255, 255))
        screen.blit(letra_surface, (90, HEIGHT // 2 - letra_surface.get_height() // 2))

        # Progreso
        progreso_txt = f"{self.aciertos} / 3"
        progreso_render = self.assets.fonts['small'].render(progreso_txt, True, (255, 255, 255))
        screen.blit(progreso_render, (WIDTH - 100, 40))

        # Base
        ficha_x = WIDTH - 195
        ficha_y = HEIGHT // 2 - 90
        screen.blit(self.ficha_base, (ficha_x, ficha_y))

        # Círculos
        for i, (x, y) in enumerate(self.puntos):
            estado = self.seleccion_usuario.get(i + 1)
            color = (13, 59, 102)
            if estado == "correcto":
                color = (0, 200, 0)
            elif estado == "incorrecto":
                color = (200, 0, 0)
            draw_circle_with_label(screen, (x, y), 24, "", self.assets.fonts['big'], color=color)

        # Barra de progreso visual
        if not self.inactividad_detectada:
            elapsed = pygame.time.get_ticks() - self.last_touch_time
            progress = min(1.0, elapsed / self.inactividad_timeout)
            bar_x = WIDTH // 2 - 50
            bar_y = HEIGHT // 2 - 90
            pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, 100, 12), border_radius=8)
            bar_color = (0, 200, 0) if progress < 0.5 else (255, 215, 0) if progress < 0.8 else (249, 87, 56)
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(100 * progress), 12), border_radius=8)

        # Botón
        pygame.draw.rect(screen, (249, 87, 56), self.evaluar_button, border_radius=10)
        texto = self.assets.fonts['default'].render("Evaluar", True, (255, 255, 255))
        text_rect = texto.get_rect(center=self.evaluar_button.center)
        screen.blit(texto, text_rect)

        if self.popup:
            self.popup.draw()