import pygame
import json
import random
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BACKGROUND_COLOR
from ui.ui_helpers import draw_text_centered, draw_circle_with_label, draw_multiline_centered, draw_pulsing_button, draw_breathing_background, create_particles, update_and_draw_particles
from ui.sidebar_menu import SidebarMenu
from ui.popup_message import PopupMessage

class MayusculasScene:
    def __init__(self, assets, progress):
        self.assets = assets
        self.progress = progress
        self.screen = pygame.display.get_surface()

        # Animación de partículas
        self.particles = create_particles(amount=30, screen_width=WIDTH, screen_height=HEIGHT)

        # Animación del botón "Siguiente"
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

        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        self.sidebar = SidebarMenu(
            labels=["Aprende", "Clasifica", "Construye", "Aplica"],
            font=self.assets.fonts['small'],
            width=160,
            height=HEIGHT
        )

        # Ejercicio "Aprende el prefijo"
        self.modo = "instruccion"  # Primer modo: instrucción
        self.puntos = [
            (180, 100), (180, 170), (180, 240),
            (300, 100), (300, 170), (300, 240)
        ]
        self.tocados_correctos = set()
        self.tocados_incorrectos = set()
        self.mostrar_feedback = ""

        # Botón "Siguiente" abajo a la derecha
        self.boton_siguiente_img = pygame.image.load(ASSETS_PATHS['buttons']['next']).convert_alpha()
        self.boton_siguiente_img = pygame.transform.smoothscale(self.boton_siguiente_img, (60, 60))
        self.boton_siguiente_rect = self.boton_siguiente_img.get_rect(topright=(WIDTH - 10, HEIGHT - 70))

        # Carga de datos de Braille
        with open('assets/data/braille_letters.json', 'r', encoding='utf-8') as f:
            self.braille_data = json.load(f)
        with open('assets/data/nombres_siglas.json', 'r', encoding='utf-8') as f:
            self.data_nombres_siglas = json.load(f)
        

        self.letras_braille = self.braille_data["letras"]
        self.mayusculas_braille = self.braille_data["mayusculas"]
        self.prefijo_mayuscula = self.braille_data["prefijos"]["mayuscula"]
        self.data_nombres_siglas["nombres_propios"]
        self.data_nombres_siglas["siglas"]


        # Variables para ejercicio 2
        self.puntos_activos = []
        self.es_mayuscula = False
        self.botones_clasifica = self._crear_botones_clasifica()
        self.feedback_clasifica = ""

        # Contador de aciertos para el ejercicio de clasificación
        self.aciertos_clasifica = 0
        self.meta_aciertos = 5  # Número de aciertos necesarios para completar el ejercicio
        # Contador de errores para el ejercicio de clasificación
        self.errores_clasifica = 0
        self.limite_errores = 3  # Errores permitidos antes de mostrar ayuda

        # Variables para el ejercicio de nombres propios Ejercicio 3
        self.nombre_actual = ""
        self.bien_escrito = True  # Si el nombre mostrado tiene o no el prefijo correcto
        self.botones_nombres = self._crear_botones_nombres()
        self.feedback_nombres = ""
        # Contador de aciertos para el ejercicio de nombres propios
        self.aciertos_nombres = 0
        self.meta_aciertos_nombres = 5  # Número de aciertos necesarios para completar el ejercicio
        # Variables para el ejercicio de siglas
        self.sigla_actual = ""
        self.es_sigla = True
        self.botones_siglas = self._crear_botones_siglas()
        self.feedback_siglas = ""
        self.aciertos_siglas = 0
        self.meta_aciertos_siglas = 5

    def on_enter(self):
        self.reset_state()

    def handle_event(self, event):
        if self.popup:
            result = self.popup.handle_event(event)
            if result == "close":
                if hasattr(self, "_reiniciar_errores"):
                    self._reiniciar_errores()
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

            if self.current_index == 0:
                if self.modo == "instruccion":
                    if self.boton_siguiente_rect.collidepoint(event.pos):
                        self.modo = "interactivo"
                else:
                    self.handle_event_aprende(event)
            elif self.current_index == 1:
                self.handle_event_clasifica(event)  # <- NUEVO: manejar clicks en ejercicio 2
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
                    self.errores_clasifica = 0  # Reiniciar errores si acierta
                    self.feedback_clasifica = "¡Correcto!"
                    self.verificar_final_clasifica()
                else:
                    self.errores_clasifica += 1
                    self.feedback_clasifica = "Incorrecto. Era mayúscula."
                    self.verificar_errores()

            elif self.botones_clasifica["mayúscula"].collidepoint(pos):
                if self.es_mayuscula:
                    self.aciertos_clasifica += 1
                    self.errores_clasifica = 0  # Reiniciar errores si acierta
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

    def verificar_final_siglas(self):
        if self.aciertos_siglas >= self.meta_aciertos_siglas:
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['default'],
                title="¡Excelente!",
                message="¡Terminaste el reto de siglas en Braille!",
                on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "Aplica en siglas"), self.next_exercise()),
                show_next=False
            )
            self.popup.show()
            self.estado = "completado"
        else:
            self.generar_sigla()

    def verificar_final_nombres(self):
        if self.aciertos_nombres >= self.meta_aciertos_nombres:
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['default'],
                title="¡Muy bien!",
                message="¡Completaste el reto de nombres propios en Braille!",
                on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "Arma nombres propios"), self.next_exercise()),
                show_next=False
            )
            self.popup.show()
            self.estado = "completado"
        else:
            self.generar_nombre_propio()


    def verificar_final_clasifica(self):
        if self.aciertos_clasifica >= self.meta_aciertos:
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['default'],
                title="¡Excelente!",
                message="¡Completaste el reto de mayúsculas y minúsculas!",
                on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "¿Minúscula o Mayúscula?"), self.next_exercise()),
                show_next=False
            )
            self.popup.show()
            self.estado = "completado"
        else:
            self.generar_nueva_clasificacion()

    def verificar_errores(self):
        if self.errores_clasifica >= self.limite_errores:
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['default'],
                title="¡Ánimo!",
                message="Recuerda: las mayúsculas llevan prefijo (puntos 4 y 6).\n¡Sigue practicando!",
                on_close=lambda: self._reiniciar_errores(),
                show_next=False
            )
            self.popup.show()
            self.estado = "en_curso" # No avanza de ejercicio, solo ayuda motivacional

    def _reiniciar_errores(self):
        self.errores_clasifica = 0
        self.feedback_clasifica = ""
        self.popup = None  # Cierra el popup
        self.generar_nueva_clasificacion()

    def mostrar_modal_prefijo(self):
        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['default'],
            title="¡Muy bien!",
            message="Los puntos 4 y 6 forman el prefijo de mayúscula en Braille.",
            on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "Aprende el prefijo"), self.next_exercise()),
            show_next=False
        )
        self.popup.show()
        self.estado = "completado"

    def _crear_botones_siglas(self):
        boton_sigla = pygame.Rect(WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        boton_normal = pygame.Rect(3*WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        return {"sigla": boton_sigla, "normal": boton_normal}
    
    def generar_sigla(self):
        siglas = self.data_nombres_siglas["siglas"]
        self.sigla_actual = random.choice(siglas)
        self.es_sigla = random.choice([True, False])

    def update(self, dt):
        self.sidebar.update(dt)
        self.tiempo_animacion += dt 

    def draw(self):
        self.screen.fill((13, 59, 102))
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['big'], 30)

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

    def draw_instruccion(self):
        draw_breathing_background(
            self.screen,
            base_color=BACKGROUND_COLOR,  # <--- aquí usamos tu constante
            tiempo=self.tiempo_animacion,
            intensidad=20,
            velocidad=1
        )

        # Dibuja las partículas
        update_and_draw_particles(self.particles, self.screen, dt=1/60)

        texto_instruccion = [
            "En Braille usamos un prefijo",
            "especial para indicar que una",
            "letra es mayúscula.",
            "",
            "Toca 'Siguiente' ",
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
                color = (0, 255, 0)  # Verde
            elif (i + 1) in self.tocados_incorrectos:
                color = (255, 0, 0)  # Rojo
            else:
                color = (255, 255, 255)  # Blanco

            draw_circle_with_label(self.screen, (x, y), 30, str(i + 1), self.assets.fonts['default'], color=color)

        if self.mostrar_feedback:
            draw_text_centered(self.screen, self.mostrar_feedback, self.assets.fonts['small'], HEIGHT - 40, (255, 255, 0))

    def _crear_botones_clasifica(self):
        """
        Crea los botones de respuesta para el ejercicio de clasificación.
        """
        boton_min = pygame.Rect(WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        boton_may = pygame.Rect(3*WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        return {"minúscula": boton_min, "mayúscula": boton_may}

    def draw_clasifica(self):
        self.screen.fill((13, 59, 102))

        # Coordenadas de las celdas
        celda_izq_x = WIDTH//2 - 120
        celda_der_x = WIDTH//2 + 20
        base_y = HEIGHT//3

        # Función para dibujar una celda
        def dibujar_celda(x_offset, puntos_activos):
            posiciones = [
                (x_offset, base_y),            # Punto 1
                (x_offset, base_y + 60),        # Punto 2
                (x_offset, base_y + 120),       # Punto 3
                (x_offset + 80, base_y),        # Punto 4
                (x_offset + 80, base_y + 60),   # Punto 5
                (x_offset + 80, base_y + 120)   # Punto 6
            ]
            for idx, (x, y) in enumerate(posiciones):
                if (idx + 1) in puntos_activos:
                    color = (255, 255, 255)  # Encendido
                else:
                    color = (150, 150, 150)  # Apagado
                pygame.draw.circle(self.screen, color, (x, y), 20)

        # Dibuja primera celda (prefijo o vacío)
        dibujar_celda(celda_izq_x, self.prefijo_puntos)

        # Dibuja segunda celda (letra)
        dibujar_celda(celda_der_x, self.letra_puntos)

        # Dibuja los botones
        min_rect = self.botones_clasifica["minúscula"]
        may_rect = self.botones_clasifica["mayúscula"]

        pygame.draw.rect(self.screen, (200, 200, 255), min_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 200, 200), may_rect, border_radius=15)

        font = self.assets.fonts['default']
        min_text = font.render("Minúscula", True, (0, 0, 0))
        may_text = font.render("Mayúscula", True, (0, 0, 0))

        self.screen.blit(min_text, (min_rect.centerx - min_text.get_width()//2, min_rect.centery - min_text.get_height()//2))
        self.screen.blit(may_text, (may_rect.centerx - may_text.get_width()//2, may_rect.centery - may_text.get_height()//2))

        # Mostrar retroalimentación
        if self.feedback_clasifica:
            draw_text_centered(self.screen, self.feedback_clasifica, self.assets.fonts['small'], HEIGHT - 30, color=(255, 255, 0))

    def draw_siglas(self):
        self.screen.fill((13, 59, 102))

        x_start = 50
        y_start = HEIGHT // 3

        posiciones_base = [
            (0, 0),
            (0, 40),
            (0, 80),
            (40, 0),
            (40, 40),
            (40, 80)
        ]

        x_actual = x_start
        y_actual = y_start
        celda_width = 90
        celda_height = 130

        for idx, letra in enumerate(self.sigla_actual):
            if x_actual + celda_width > WIDTH - 50:
                x_actual = x_start
                y_actual += celda_height

            # Prefijo
            if self.es_sigla or (idx == 0 and not self.es_sigla):
                for i, (dx, dy) in enumerate(posiciones_base):
                    punto = i + 1
                    if punto in self.prefijo_mayuscula:
                        color = (255, 255, 255)
                    else:
                        color = (150, 150, 150)
                    pygame.draw.circle(self.screen, color, (x_actual + dx, y_actual + dy), 12)
                x_actual += celda_width

            # Letra
            puntos = self.letras_braille.get(letra.lower(), [])
            for i, (dx, dy) in enumerate(posiciones_base):
                punto = i + 1
                if punto in puntos:
                    color = (255, 255, 255)
                else:
                    color = (150, 150, 150)
                pygame.draw.circle(self.screen, color, (x_actual + dx, y_actual + dy), 12)
            x_actual += celda_width

        # Botones
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
            draw_text_centered(self.screen, self.feedback_siglas, self.assets.fonts['small'], HEIGHT - 30, color=(255, 255, 0))

    def generar_nueva_clasificacion(self):
        letras = list(self.letras_braille.keys())
        letra = random.choice(letras)
        self.es_mayuscula = random.choice([True, False])

        if self.es_mayuscula:
            may = letra.upper()
            if may in self.mayusculas_braille:
                prefijo, letra_puntos = self.mayusculas_braille[may]
                self.prefijo_puntos = prefijo  # Guardar prefijo
                self.letra_puntos = letra_puntos  # Guardar puntos de la letra
            else:
                self.prefijo_puntos = []
                self.letra_puntos = []
        else:
            self.prefijo_puntos = []  # Nada en prefijo
            self.letra_puntos = self.letras_braille.get(letra, [])

    def draw_nombres(self):
        self.screen.fill((13, 59, 102))

        x_start = 50  # Margen inicial izquierdo
        y_start = HEIGHT // 3

        posiciones_base = [
            (0, 0),
            (0, 40),
            (0, 80),
            (40, 0),
            (40, 40),
            (40, 80)
        ]

        x_actual = x_start
        y_actual = y_start
        celda_width = 90  # Nuevo ancho por celda
        celda_height = 130  # Nuevo alto por celda

        # Dibujar prefijo si corresponde
        if self.bien_escrito:
            for idx, (dx, dy) in enumerate(posiciones_base):
                punto = idx + 1
                if punto in self.prefijo_mayuscula:
                    color = (255, 255, 255)
                else:
                    color = (150, 150, 150)
                pygame.draw.circle(self.screen, color, (x_actual + dx, y_actual + dy), 12)
            x_actual += celda_width

        # Dibujar letras del nombre
        for letra in self.nombre_actual:
            if x_actual + celda_width > WIDTH - 50:  # Si se va a salir
                x_actual = x_start
                y_actual += celda_height  # Baja una fila

            puntos = self.letras_braille.get(letra.lower(), [])
            for idx, (dx, dy) in enumerate(posiciones_base):
                punto = idx + 1
                if punto in puntos:
                    color = (255, 255, 255)
                else:
                    color = (150, 150, 150)
                pygame.draw.circle(self.screen, color, (x_actual + dx, y_actual + dy), 12)
            x_actual += celda_width

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

        if self.feedback_nombres:
            draw_text_centered(self.screen, self.feedback_nombres, self.assets.fonts['small'], HEIGHT - 30, color=(255, 255, 0))

    def _crear_botones_nombres(self):
        boton_bien = pygame.Rect(WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        boton_mal = pygame.Rect(3*WIDTH//4 - 75, HEIGHT - 120, 150, 60)
        return {"bien": boton_bien, "mal": boton_mal}
    
    def generar_nombre_propio(self):
        nombres = self.data_nombres_siglas["nombres_propios"]
        self.nombre_actual = random.choice(nombres)
        self.bien_escrito = random.choice([True, False])

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
        self.modo = "instruccion"
        self.errores_clasifica = 0
        self.aciertos_clasifica = 0  # Reiniciar aciertos
        self.aciertos_nombres = 0 
        self.feedback_siglas = ""
        self.aciertos_siglas = 0

        # Genera letra Braille nueva al entrar al ejercicio 2
        if self.current_index == 1:
            self.generar_nueva_clasificacion()
        if self.current_index == 2:
            self.generar_nombre_propio()
        if self.current_index == 3:
            self.generar_sigla()
