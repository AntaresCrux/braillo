import pygame
import random
import json
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BACKGROUND_COLOR, AMARILLO_PASTEL, BLANCO, VERDE, NARANJA
from ui.ui_helpers import draw_text_centered, draw_progress_text, draw_multiline_centered
from ui.sidebar_menu import SidebarMenu
from ui.popup_message import PopupMessage

class SignosScene:
    def __init__(self, assets, progress):
        self.assets = assets
        self.progress = progress
        self.screen = pygame.display.get_surface()

        self.signos = list(ASSETS_PATHS['fichas']['signos'].keys())

        # Cargar frases desde JSON
        with open('assets/data/signos_frases.json', 'r', encoding='utf-8') as f:
            self.frases = json.load(f)

        self.total_intentos = 0
        self.aciertos = 0
        self.current_index = 0  # 0 = Reconoce, 1 = Completa frase

        self.signo_actual = ""
        self.frase_actual = None
        self.seleccion_usuario = None
        self.estado_validacion = False
        self.mensaje_resultado = ""

        self.esperando_nuevo = False
        self.tiempo_validacion = 0

        # Botones
        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        self.check_icon = pygame.image.load(ASSETS_PATHS['buttons']['check']).convert_alpha()
        self.check_icon = pygame.transform.smoothscale(self.check_icon, (60, 60))
        self.palomita_rect = self.check_icon.get_rect(topright=(WIDTH - 10, HEIGHT - 70))

        self.sidebar = SidebarMenu(
            labels=["Reconoce", "Completa frase"],
            font=self.assets.fonts['small'],
            width=240,
            height=HEIGHT
        )
        self.sombra_sidebar = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.sombra_sidebar.fill((0, 0, 0, 100))

        self.popup = None

        self.generar_nuevo()

    def handle_event(self, event):
        if self.popup:
            result = self.popup.handle_event(event)
            if result == "close":
                self.popup = None
                return "popup_closed"
            return

        if self.sidebar.visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_button_rect.collidepoint(event.pos):
                    self.sidebar.toggle()
                    return
                sidebar_index = self.sidebar.handle_event(event)
                if sidebar_index is not None:
                    self.switch_exercise(sidebar_index)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_button_rect.collidepoint(event.pos):
                self.sidebar.toggle()
                return
            if self.back_icon_rect.collidepoint(event.pos):
                self.reset_state()
                return "select_level"

            if self.palomita_rect.collidepoint(event.pos):
                if not self.estado_validacion:
                    self.validar_respuesta()
                return

            for signo, rect in self.rects_fichas.items():
                if rect.collidepoint(event.pos):
                    self.seleccion_usuario = signo
                    break

    def update(self, dt):
        self.sidebar.update(dt)

        if self.esperando_nuevo:
            self.tiempo_validacion += dt
            if self.tiempo_validacion >= 1:
                if self.total_intentos >= 10:
                    self.mostrar_popup_final()
                else:
                    self.generar_nuevo()
                self.esperando_nuevo = False

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        if self.current_index == 0:
            draw_text_centered(
                surface=self.screen,
                text=self.signo_actual,
                font=self.assets.fonts['big'],
                x=232,
                y=21,
                color=BLANCO
            )
        elif self.current_index == 1:
            draw_text_centered(
                surface=self.screen,
                text=self.frase_actual["texto"],
                font=self.assets.fonts['small'],
                x=75,
                y=30,
                color=BLANCO
            )

        draw_progress_text(
            surface=self.screen,
            font=self.assets.fonts['tiny'],
            current=self.total_intentos,
            total=10,
            x=334,
            y=50,
            color=AMARILLO_PASTEL
        )

        # Fichas
        self.rects_fichas = {}
        x_inicial = 80
        y_inicial = 110
        espacio_x = 60
        espacio_y = 60

        for i, signo in enumerate(self.signos):
            fila = i // 6
            columna = i % 6
            x = x_inicial + columna * espacio_x
            y = y_inicial + fila * espacio_y

            img = pygame.image.load(ASSETS_PATHS['fichas']['signos'][signo]).convert_alpha()
            rect = img.get_rect(topleft=(x, y))
            self.screen.blit(img, rect.topleft)

            self.rects_fichas[signo] = rect

            if signo == self.seleccion_usuario:
                pygame.draw.rect(self.screen, AMARILLO_PASTEL, rect.inflate(6, 6), 3)

        self.screen.blit(self.check_icon, self.palomita_rect.topleft)

        if self.sidebar.visible:
            self.screen.blit(self.sombra_sidebar, (0, 0))
            self.sidebar.draw(self.screen)

        self.screen.blit(self.menu_icon, self.menu_button_rect.topleft)
        self.screen.blit(self.back_icon, self.back_icon_rect.topleft)

        if self.estado_validacion:
            color = VERDE if self.mensaje_resultado == "Correcto" else NARANJA
            draw_text_centered(
                surface=self.screen,
                text=self.mensaje_resultado,
                font=self.assets.fonts['small'],
                y=82,
                color=color,
                x=197
            )

        if self.popup:
            self.popup.draw()

        pygame.display.flip()

    def generar_nuevo(self):
        if self.current_index == 0:
            self.signo_actual = random.choice(self.signos)
        else:
            self.frase_actual = random.choice(self.frases)

        self.seleccion_usuario = None
        self.estado_validacion = False
        self.mensaje_resultado = ""

    def validar_respuesta(self):
        correcto = False
        if self.current_index == 0:
            correcto = (self.seleccion_usuario == self.signo_actual)
        else:
            correcto = (self.seleccion_usuario == self.frase_actual["respuesta"])

        if correcto:
            self.mensaje_resultado = "Correcto"
            self.aciertos += 1
        else:
            self.mensaje_resultado = "Incorrecto"

        self.total_intentos += 1
        self.estado_validacion = True
        self.esperando_nuevo = True
        self.tiempo_validacion = 0

    def mostrar_popup_final(self):
        if self.aciertos >= 7:
            mensaje = "¡Excelente trabajo!"
        else:
            mensaje = "¡Intenta de nuevo!"

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['default'],
            font_text=self.assets.fonts['small'],
            title=mensaje,
            message=f"Aciertos: {self.aciertos}/10",
            on_close=self.reiniciar_juego,
            show_next=False
        )
        self.popup.show()

    def reiniciar_juego(self):
        if self.aciertos >= 7:
            if self.current_index == 0:
                self.progress.mark_exercise_done("basico_1", "signos", "Reconocimiento de signos")
            else:
                self.progress.mark_exercise_done("basico_1", "signos", "Completar frases")
            return "select_level"
        else:
            self.total_intentos = 0
            self.aciertos = 0
            self.generar_nuevo()

    def reset_state(self):
        self.popup = None
        self.total_intentos = 0
        self.aciertos = 0
        self.generar_nuevo()

    def switch_exercise(self, index):
        self.current_index = index
        self.reset_state()
