import pygame
import json
import random
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BACKGROUND_COLOR, BLANCO
from ui.ui_helpers import draw_text_centered, draw_circle_with_label, draw_multiline_centered, draw_pulsing_button, draw_breathing_background, create_particles, update_and_draw_particles, draw_braille_cell, draw_braille_word
from ui.sidebar_menu import SidebarMenu
from ui.popup_message import PopupMessage

class MayusculasScene:
    def __init__(self, assets, progress):
        self.assets = assets
        self.progress = progress
        self.screen = pygame.display.get_surface()

        self.particles = create_particles(amount=30, screen_width=WIDTH, screen_height=HEIGHT)
        self.tiempo_animacion = 0
        self.boton_siguiente_base_size = (60, 60)

        self.ejercicios = [
            "Aprende el prefijo",
            "¿Minúscula o Mayúscula?",
            "Arma nombres propios",
            "Aplica en siglas"
        ]
        self.current_index = 0
        self.estado = "en_curso"
        self.popup = None

        # UI Elements
        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        self.sidebar = SidebarMenu(
            labels=["Aprende", "Clasifica", "Construye", "Aplica"],
            font=self.assets.fonts['small'],
            width=240,
            height=HEIGHT
        )

        self.boton_siguiente_img = pygame.image.load(ASSETS_PATHS['buttons']['next']).convert_alpha()
        self.boton_siguiente_img = pygame.transform.smoothscale(self.boton_siguiente_img, (60, 60))
        self.boton_siguiente_rect = self.boton_siguiente_img.get_rect(topright=(WIDTH - 10, HEIGHT - 70))

        # Cargamos los datos de Braille
        with open('assets/data/braille_letters.json', 'r', encoding='utf-8') as f:
            self.braille_data = json.load(f)
        with open('assets/data/nombres_siglas.json', 'r', encoding='utf-8') as f:
            self.data_nombres_siglas = json.load(f)

        self.letras_braille = self.braille_data["letras"]
        self.mayusculas_braille = self.braille_data["mayusculas"]
        self.prefijo_mayuscula = self.braille_data["prefijos"]["mayuscula"]

        # Variables de los ejercicios
        self.puntos = [(180, 100), (180, 170), (180, 240), (300, 100), (300, 170), (300, 240)]
        self.modo = "instruccion"
        self.tocados_correctos = set()
        self.tocados_incorrectos = set()
        self.mostrar_feedback = ""

        self.botones_clasifica = self._crear_botones_clasifica()
        self.botones_nombres = self._crear_botones_nombres()
        self.botones_siglas = self._crear_botones_siglas()

        self.feedback_clasifica = ""
        self.feedback_nombres = ""
        self.feedback_siglas = ""

        self.aciertos_clasifica = 0
        self.aciertos_nombres = 0
        self.aciertos_siglas = 0

        self.meta_aciertos = 5
        self.meta_aciertos_nombres = 5
        self.meta_aciertos_siglas = 5

        self.errores_clasifica = 0
        self.limite_errores = 3

        self.prefijo_puntos = []
        self.letra_puntos = []

        self.nombre_actual = ""
        self.bien_escrito = True

        self.sigla_actual = ""
        self.es_sigla = True

    def on_enter(self):
        self.reset_state()

    def handle_event(self, event):
        if self.popup:
            result = self.popup.handle_event(event)
            if result == "close":
                self.popup = None
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
                return "select_level"

            # Según el ejercicio actual
            if self.current_index == 0:
                if self.modo == "instruccion":
                    if self.boton_siguiente_rect.collidepoint(event.pos):
                        self.modo = "interactivo"
                else:
                    self.handle_event_aprende(event)
            elif self.current_index == 1:
                self.handle_event_clasifica(event)
            elif self.current_index == 2:
                self.handle_event_nombres(event)
            elif self.current_index == 3:
                self.handle_event_siglas(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.next_exercise()
            elif event.key == pygame.K_LEFT:
                self.prev_exercise()

    def handle_event_aprende(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (x, y) in enumerate(self.puntos):
                rect = pygame.Rect(x - 20, y - 20, 40, 40)
                if rect.collidepoint(event.pos):
                    punto = i + 1
                    if punto in {4, 6}:
                        self.tocados_correctos.add(punto)
                        self.mostrar_feedback = "¡Correcto!"
                    else:
                        self.tocados_incorrectos.add(punto)
                        self.mostrar_feedback = "No es este, intenta otro."

            if {4, 6}.issubset(self.tocados_correctos):
                self.mostrar_modal_prefijo()

    def handle_event_clasifica(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.botones_clasifica["minúscula"].collidepoint(pos):
                if not self.es_mayuscula:
                    self.aciertos_clasifica += 1
                    self.errores_clasifica = 0
                    self.feedback_clasifica = "¡Correcto!"
                    self.verificar_final_clasifica()
                else:
                    self.errores_clasifica += 1
                    self.feedback_clasifica = "Incorrecto. Era mayúscula."
                    self.verificar_errores()
            elif self.botones_clasifica["mayúscula"].collidepoint(pos):
                if self.es_mayuscula:
                    self.aciertos_clasifica += 1
                    self.errores_clasifica = 0
                    self.feedback_clasifica = "¡Correcto!"
                    self.verificar_final_clasifica()
                else:
                    self.errores_clasifica += 1
                    self.feedback_clasifica = "Incorrecto. Era minúscula."
                    self.verificar_errores()

    def handle_event_nombres(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.botones_nombres["bien"].collidepoint(pos):
                if self.bien_escrito:
                    self.aciertos_nombres += 1
                    self.feedback_nombres = "¡Correcto!"
                    self.verificar_final_nombres()
                else:
                    self.feedback_nombres = "Incorrecto. Faltaba prefijo."
            elif self.botones_nombres["mal"].collidepoint(pos):
                if not self.bien_escrito:
                    self.aciertos_nombres += 1
                    self.feedback_nombres = "¡Correcto!"
                    self.verificar_final_nombres()
                else:
                    self.feedback_nombres = "Incorrecto. Estaba bien escrito."

    def handle_event_siglas(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.botones_siglas["sigla"].collidepoint(pos):
                if self.es_sigla:
                    self.aciertos_siglas += 1
                    self.feedback_siglas = "¡Correcto!"
                    self.verificar_final_siglas()
                else:
                    self.feedback_siglas = "Incorrecto. Era una palabra."
            elif self.botones_siglas["normal"].collidepoint(pos):
                if not self.es_sigla:
                    self.aciertos_siglas += 1
                    self.feedback_siglas = "¡Correcto!"
                    self.verificar_final_siglas()
                else:
                    self.feedback_siglas = "Incorrecto. Era una sigla."

    #VERIFICACIONES Y MODAL

    def mostrar_modal_prefijo(self):
        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title="¡Muy bien!",
            message="Los puntos 4 y 6 forman el prefijo.",
            on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "Aprende el prefijo"), self.next_exercise()),
            show_next=False
        )
        self.popup.show()
        self.estado = "completado"

    def verificar_final_clasifica(self):
        if self.aciertos_clasifica >= self.meta_aciertos:
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['small'],
                title="¡Excelente!",
                message="¡Completaste el reto!",
                on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "¿Minúscula o Mayúscula?"), self.next_exercise()),
                show_next=False
            )
            self.popup.show()
            self.estado = "completado"
        else:
            self.generar_nueva_clasificacion()

    def verificar_final_nombres(self):
        if self.aciertos_nombres >= self.meta_aciertos_nombres:
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['small'],
                title="¡Muy bien!",
                message="¡Completaste el ejercicio!",
                on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "Arma nombres propios"), self.next_exercise()),
                show_next=False
            )
            self.popup.show()
            self.estado = "completado"
        else:
            self.generar_nombre_propio()

    def verificar_final_siglas(self):
        if self.aciertos_siglas >= self.meta_aciertos_siglas:
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['small'],
                title="¡Excelente!",
                message="¡Terminaste el reto de siglas!",
                on_close=lambda: self._mostrar_popup_final(),
                show_next=False
            )
            self.popup.show()
            self.estado = "completado"
        else:
            self.generar_sigla()

    def _mostrar_popup_final(self):
        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title="¡Felicidades!",
            message="Has completado toda la sección de MAYÚSCULAS.\n\n¡Gran trabajo!",
            on_close=lambda: self.switch_exercise(0),
            show_next=False
        )
        self.popup.show()

    def verificar_errores(self):
        if self.errores_clasifica >= self.limite_errores:
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['small'],
                title="¡Ánimo!",
                message="Recuerda: las mayúsculas llevan prefijo (puntos 4 y 6).\n¡Sigue practicando!",
                on_close=lambda: self._reiniciar_errores(),
                show_next=False
            )
            self.popup.show()

    def _reiniciar_errores(self):
        self.errores_clasifica = 0
        self.feedback_clasifica = ""
        self.popup = None
        self.generar_nueva_clasificacion()

    #Actualizaciones y dibujo

    def update(self, dt):
        self.sidebar.update(dt)
        self.tiempo_animacion += dt

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['default'], 22, color=BLANCO)

        if self.current_index == 0:
            if self.modo == "instruccion":
                self.draw_instruccion()
            else:
                self.draw_aprende()
        elif self.current_index == 1:
            self.draw_clasifica()
        elif self.current_index == 2:
            self.draw_nombres()
        elif self.current_index == 3:
            self.draw_siglas()

        if self.sidebar.visible:
            sombra = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 100))
            self.screen.blit(sombra, (0, 0))
            self.sidebar.draw(self.screen)

        self.screen.blit(self.menu_icon, self.menu_button_rect.topleft)
        self.screen.blit(self.back_icon, self.back_icon_rect.topleft)

        if self.popup:
            self.popup.draw()

        pygame.display.flip()

        #Botones

    def _crear_botones_clasifica(self):
        boton_min = pygame.Rect(WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        boton_may = pygame.Rect(3*WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        return {"minúscula": boton_min, "mayúscula": boton_may}

    def _crear_botones_nombres(self):
        boton_bien = pygame.Rect(WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        boton_mal = pygame.Rect(3*WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        return {"bien": boton_bien, "mal": boton_mal}

    def _crear_botones_siglas(self):
        boton_sigla = pygame.Rect(WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        boton_normal = pygame.Rect(3*WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        return {"sigla": boton_sigla, "normal": boton_normal}

    # --- GENERAR CONTENIDO NUEVO ---

    def generar_nueva_clasificacion(self):
        letras = list(self.letras_braille.keys())
        letra = random.choice(letras)
        self.es_mayuscula = random.choice([True, False])

        if self.es_mayuscula:
            may = letra.upper()
            if may in self.mayusculas_braille:
                prefijo, letra_puntos = self.mayusculas_braille[may]
                self.prefijo_puntos = prefijo
                self.letra_puntos = letra_puntos
            else:
                self.prefijo_puntos = []
                self.letra_puntos = []
        else:
            self.prefijo_puntos = []
            self.letra_puntos = self.letras_braille.get(letra, [])

    def generar_nombre_propio(self):
        nombres = self.data_nombres_siglas["nombres_propios"]
        self.nombre_actual = random.choice(nombres)
        self.bien_escrito = random.choice([True, False])

    def generar_sigla(self):
        siglas = self.data_nombres_siglas["siglas"]
        self.sigla_actual = random.choice(siglas)
        self.es_sigla = random.choice([True, False])

    #CAMBIAR DE EJERCICIO O RESETEAR ESTADO

    def switch_exercise(self, index):
        self.current_index = index
        self.reset_state()

    def next_exercise(self):
        if self.current_index < len(self.ejercicios) - 1:
            self.current_index += 1
            self.reset_state()

    def prev_exercise(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.reset_state()

    def reset_state(self):
        self.estado = "en_curso"
        self.popup = None
        self.tocados_correctos.clear()
        self.tocados_incorrectos.clear()
        self.mostrar_feedback = ""
        self.feedback_clasifica = ""
        self.feedback_nombres = ""
        self.feedback_siglas = ""
        self.modo = "instruccion"
        self.errores_clasifica = 0
        self.aciertos_clasifica = 0
        self.aciertos_nombres = 0
        self.aciertos_siglas = 0

        # Reiniciar contenido al cambiar de ejercicio
        if self.current_index == 1:
            self.generar_nueva_clasificacion()
        if self.current_index == 2:
            self.generar_nombre_propio()
        if self.current_index == 3:
            self.generar_sigla()

        #DIBUJAR ESCENAS DE EJERCICIO

    def draw_instruccion(self):
        draw_breathing_background(
            self.screen,
            base_color=BACKGROUND_COLOR,
            tiempo=self.tiempo_animacion,
            intensidad=20,
            velocidad=1
        )

        update_and_draw_particles(self.particles, self.screen, dt=1/60)

        texto_instruccion = [
            "En Braille usamos un prefijo",
            "especial para indicar que una",
            "letra es mayúscula.",
            "",
            "Toca 'Siguiente'",
            "para aprender cuáles son los puntos."
        ]

        font = self.assets.fonts['small']
        draw_multiline_centered(self.screen, texto_instruccion, font, y_start=HEIGHT//4, line_spacing=25)

        draw_pulsing_button(
            self.screen,
            self.boton_siguiente_img,
            (WIDTH - 40, HEIGHT - 40),
            self.tiempo_animacion,
            self.boton_siguiente_base_size,
            pulso_amplitud=0.08,
            pulso_velocidad=3
        )

    def draw_aprende(self):
        for i, (x, y) in enumerate(self.puntos):
            if (i + 1) in self.tocados_correctos:
                color = (0, 255, 0)
            elif (i + 1) in self.tocados_incorrectos:
                color = (255, 0, 0)
            else:
                color = (255, 255, 255)

            draw_circle_with_label(self.screen, (x, y), 30, str(i + 1), self.assets.fonts['default'], color=color)

        if self.mostrar_feedback:
            draw_text_centered(self.screen, self.mostrar_feedback, self.assets.fonts['small'], HEIGHT - 40, (255, 255, 0))

    def draw_clasifica(self):
        self.screen.fill(BACKGROUND_COLOR)

        celda_izq_x = WIDTH//2 - 120
        celda_der_x = WIDTH//2 + 20
        base_y = HEIGHT//3

        def dibujar_celda(x_offset, puntos_activos):
            posiciones = [
                (x_offset, base_y),
                (x_offset, base_y + 60),
                (x_offset, base_y + 120),
                (x_offset + 80, base_y),
                (x_offset + 80, base_y + 60),
                (x_offset + 80, base_y + 120)
            ]
            for idx, (x, y) in enumerate(posiciones):
                if (idx + 1) in puntos_activos:
                    color = (255, 255, 255)
                else:
                    color = (150, 150, 150)
                pygame.draw.circle(self.screen, color, (x, y), 20)

        dibujar_celda(celda_izq_x, self.prefijo_puntos)
        dibujar_celda(celda_der_x, self.letra_puntos)

        min_rect = self.botones_clasifica["minúscula"]
        may_rect = self.botones_clasifica["mayúscula"]

        pygame.draw.rect(self.screen, (200, 200, 255), min_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 200, 200), may_rect, border_radius=15)

        font = self.assets.fonts['default']
        min_text = font.render("Minúscula", True, (0, 0, 0))
        may_text = font.render("Mayúscula", True, (0, 0, 0))

        self.screen.blit(min_text, (min_rect.centerx - min_text.get_width()//2, min_rect.centery - min_text.get_height()//2))
        self.screen.blit(may_text, (may_rect.centerx - may_text.get_width()//2, may_rect.centery - may_text.get_height()//2))

        if self.feedback_clasifica:
            draw_text_centered(self.screen, self.feedback_clasifica, self.assets.fonts['small'], HEIGHT - 30, (255, 255, 0))

    def draw_nombres(self):
        self.screen.fill((13, 59, 102))

        x_start = 50             # Margen izquierdo inicial
        y_start = HEIGHT // 3

        # Si el nombre debe llevar prefijo
        if self.bien_escrito:
            # Dibujamos el prefijo (puntos 4 y 6)
            draw_braille_cell(
                surface=self.screen,
                puntos_activos=self.prefijo_mayuscula,
                x=x_start,
                y=y_start,
                radio=8,
                separacion_horizontal=37,
                separacion_vertical=30
            )
            # Movemos el inicio para la palabra 
            x_start += 90 

        # Dibujamos nombres propios en Braille
        draw_braille_word(
            surface=self.screen,
            palabra=self.nombre_actual,
            braille_data=self.letras_braille,
            x_start=x_start,
            y_start=y_start,
            max_width=WIDTH - 50,
            radio=8,
            separacion_horizontal=37,
            separacion_vertical=30,
            espacio_letra=20
        )

        # Dibujar botones
        bien_rect = self.botones_nombres["bien"]
        mal_rect = self.botones_nombres["mal"]

        pygame.draw.rect(self.screen, (200, 255, 200), bien_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 200, 200), mal_rect, border_radius=15)

        font = self.assets.fonts['default']
        bien_text = font.render("Está bien", True, (0, 0, 0))
        mal_text = font.render("Falta prefijo", True, (0, 0, 0))

        self.screen.blit(bien_text, (bien_rect.centerx - bien_text.get_width()//2, bien_rect.centery - bien_text.get_height()//2))
        self.screen.blit(mal_text, (mal_rect.centerx - mal_text.get_width()//2, mal_rect.centery - mal_text.get_height()//2))

        # Feedback de respuesta
        if self.feedback_nombres:
            draw_text_centered(self.screen, self.feedback_nombres, self.assets.fonts['small'], HEIGHT - 30, color=(255, 255, 0))

    def draw_siglas(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Dibuja la sigla o palabra en Braille
        draw_braille_word(
            surface=self.screen,
            palabra=self.sigla_actual,
            braille_data=self.letras_braille,
            x_start=50,
            y_start=HEIGHT // 3,
            max_width=WIDTH - 50,
            radio=8,
            separacion_horizontal=37,
            separacion_vertical=30,
            espacio_letra=20,
            incluir_prefijo=self.es_sigla
        )

        # Botones de opciones
        sigla_rect = self.botones_siglas["sigla"]
        normal_rect = self.botones_siglas["normal"]

        pygame.draw.rect(self.screen, (200, 255, 200), sigla_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 200, 200), normal_rect, border_radius=15)

        font = self.assets.fonts['default']
        sigla_text = font.render("Es Sigla", True, (0, 0, 0))
        normal_text = font.render("Es Palabra", True, (0, 0, 0))

        self.screen.blit(sigla_text, (sigla_rect.centerx - sigla_text.get_width()//2, sigla_rect.centery - sigla_text.get_height()//2))
        self.screen.blit(normal_text, (normal_rect.centerx - normal_text.get_width()//2, normal_rect.centery - normal_text.get_height()//2))

        if self.feedback_siglas:
            draw_text_centered(self.screen, self.feedback_siglas, self.assets.fonts['small'], HEIGHT - 30, (255, 255, 0))
