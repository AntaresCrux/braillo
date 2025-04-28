import pygame
import json
import random
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BACKGROUND_COLOR, AMARILLO_PASTEL, BLANCO, ROJO, NARANJA, VERDE
from ui.ui_helpers import draw_text_centered, draw_circle_with_label, draw_multiline_centered, draw_pulsing_button, draw_breathing_background, create_particles, update_and_draw_particles, draw_progress_text
from ui.sidebar_menu import SidebarMenu
from ui.popup_message import PopupMessage

class NumerosScene:
    def __init__(self, assets, progress):
        self.assets = assets
        self.progress = progress
        self.screen = pygame.display.get_surface()

        self.particles = create_particles(amount=30, screen_width=WIDTH, screen_height=HEIGHT)
        self.tiempo_animacion = 0
        self.boton_siguiente_base_size = (60, 60)

        self.ejercicios = [
            "Aprende el prefijo",
            "Traduce números",
            "Escribe un número"
        ]
        self.current_index = 0
        self.estado = "en_curso"
        self.popup = None

        # Crear sombra del sidebar una vez
        self.sombra_sidebar = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.sombra_sidebar.fill((0, 0, 0, 100))

        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        self.sidebar = SidebarMenu(
            labels=["Aprende", "Traduce", "Escribe"],
            font=self.assets.fonts['small'],
            width=240,
            height=HEIGHT
        )

        self.boton_siguiente_img = pygame.image.load(ASSETS_PATHS['buttons']['next']).convert_alpha()
        self.boton_siguiente_img = pygame.transform.smoothscale(self.boton_siguiente_img, (60, 60))
        self.boton_siguiente_rect = self.boton_siguiente_img.get_rect(topright=(WIDTH - 10, HEIGHT - 70))

        with open('assets/data/braille_letters.json', 'r', encoding='utf-8') as f:
            self.braille_data = json.load(f)

        self.prefijo_numero = self.braille_data["prefijos"]["numero"]
        self.letras_braille = self.braille_data["letras"]

        # Variables para el primer ejercicio
        self.puntos = [(180, 100), (180, 170), (180, 240), (300, 100), (300, 170), (300, 240)]
        self.modo = "instruccion"
        self.tocados_correctos = set()
        self.tocados_incorrectos = set()
        self.mostrar_feedback = ""

        # Variables para ejercicio: Traduce el número
        self.numero_actual = ""              # Número aleatorio que aparece
        self.puntos_seleccionados = set()     # Puntos que el usuario toca
        self.mensaje_resultado = ""           # Mensaje de correcto o incorrecto
        self.estado_validacion = False        # True cuando ya validó
        self.numeros_braille = self.braille_data["numeros"]  # Cargar números del JSON

        self.check_icon = pygame.image.load(ASSETS_PATHS['buttons']['check']).convert_alpha()
        self.check_icon = pygame.transform.smoothscale(self.check_icon, (60, 60))
        self.tiempo_validacion = 0  # Cuánto tiempo ha pasado después de validar
        self.esperando_nuevo_numero = False  # Bandera para saber si estamos esperando

        self.total_intentos_traduce = 0  # Intentos que lleva en el ejercicio 2
        self.aciertos_traduce = 0        # Aciertos que lleva en el ejercicio 2
        self.tiempo_validacion = 0       # Tiempo que pasa después de validar
        self.esperando_nuevo_numero = False  # True si está esperando para mostrar nuevo número
        self.esperando_nuevo_numero_escribe = False

        # Variables para ejercicio: Escribe el número
        self.total_intentos_escribe = 0
        self.aciertos_escribe = 0

    def on_enter(self):
        self.reset_state()

    def handle_event(self, event):
        if self.popup:
            result = self.popup.handle_event(event)
            if result == "close":
                self.popup = None
                return "popup_closed"  # <- Muy importante
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
                    self.handle_event_aprende()
            elif self.current_index == 1:
                self.handle_event_traduce(event)
            elif self.current_index == 2:
                if self.modo == "instruccion":
                    if self.boton_siguiente_rect.collidepoint(event.pos):
                        self.modo = "interactivo"
                        #self.reset_state() 
                else:
                    self.handle_event_escribe(event)
            elif self.current_index == 3:
                self.handle_event_quiz(event)


    def handle_event_aprende(self):
        pos = pygame.mouse.get_pos()
        for i, (x, y) in enumerate(self.puntos):
            rect = pygame.Rect(x - 20, y - 20, 40, 40)
            if rect.collidepoint(pos):
                punto = i + 1
                if punto in self.prefijo_numero:
                    self.tocados_correctos.add(punto)
                    self.mostrar_feedback = "¡Correcto!"
                else:
                    self.tocados_incorrectos.add(punto)
                    self.mostrar_feedback = "No es este, prueba otro."

        if set(self.prefijo_numero).issubset(self.tocados_correctos):
            self.mostrar_modal_prefijo()

    def handle_event_traduce(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # --- Detectar clic en botón de regreso ---
            if self.back_icon_rect.collidepoint(pos):
                return "select_level"  # Volver al selector de niveles

            # --- Detectar clic en palomita ---
            if hasattr(self, 'palomita_rect') and self.palomita_rect.collidepoint(pos):
                if not self.estado_validacion:
                    self.validar_traduccion()
                else:
                    self.generar_nuevo_numero()
                return

            # --- Detectar clic en los puntos Braille ---
            x_inicio_celda = self.back_icon_rect.right + 32
            puntos_posiciones = [
                (x_inicio_celda, 130),
                (x_inicio_celda, 200),
                (x_inicio_celda, 270),
                (x_inicio_celda + 80, 130),
                (x_inicio_celda + 80, 200),
                (x_inicio_celda + 80, 270)
            ]

            for i, (x, y) in enumerate(puntos_posiciones):
                rect = pygame.Rect(x - 20, y - 20, 40, 40)
                if rect.collidepoint(pos):
                    punto_numero = i + 1
                    if punto_numero in self.puntos_seleccionados:
                        self.puntos_seleccionados.remove(punto_numero)  # Deseleccionar si ya estaba
                    else:
                        self.puntos_seleccionados.add(punto_numero)      # Seleccionar si no estaba

    def mostrar_modal_prefijo(self):
        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['tiny'],
            title="¡Muy bien!",
            message="Los puntos 3, 4, 5 y 6 forman el prefijo de número.",
            on_close=lambda: (self.progress.mark_exercise_done("basico_1", "numeros", "Aprende el prefijo"), self.next_exercise()),
            show_next=False
        )
        self.popup.show()
        self.estado = "completado"

    def update(self, dt):
        self.sidebar.update(dt)
        self.tiempo_animacion += dt

        if self.esperando_nuevo_numero:
            self.tiempo_validacion += dt
            if self.tiempo_validacion >= 1:  # Espera 1 segundo después de validar
                if self.total_intentos_traduce >= 10:
                    self.mostrar_popup_final_traduce()
                else:
                    self.generar_nuevo_numero()
                    self.esperando_nuevo_numero = False
                    self.estado_validacion = False

        if self.esperando_nuevo_numero_escribe:
            self.tiempo_validacion_escribe += dt
            if self.tiempo_validacion_escribe >= 1:
                if self.total_intentos_escribe >= 10:
                    self.mostrar_popup_final_escribe()
                else:
                    self.generar_nuevo_numero_escribe()
                self.esperando_nuevo_numero_escribe = False

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        if self.current_index == 0:
            if self.modo == "instruccion":
                self.draw_instruccion()
            else:
                self.draw_aprende()
        elif self.current_index == 1:
            self.draw_traduce()
        elif self.current_index == 2:
            if self.modo == "instruccion":
                self.draw_instruccion_escribe()
            else:
                self.draw_escribe()

        elif self.current_index == 3:
            self.draw_quiz()

        if self.sidebar.visible:
            self.screen.blit(self.sombra_sidebar, (0, 0))
            self.sidebar.draw(self.screen)

        self.screen.blit(self.menu_icon, self.menu_button_rect.topleft)
        self.screen.blit(self.back_icon, self.back_icon_rect.topleft)

        if self.popup:
            self.popup.draw()

        pygame.display.flip()

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
            "especial para indicar números.",
            "",
            "Toca 'Siguiente'",
            "para aprender cuáles son los puntos."
        ]
        draw_multiline_centered(self.screen, texto_instruccion, self.assets.fonts['small'], y_start=HEIGHT//4, line_spacing=25)

        draw_pulsing_button(
            self.screen,
            self.boton_siguiente_img,
            (WIDTH - 40, HEIGHT - 40),
            self.tiempo_animacion,
            self.boton_siguiente_base_size,
            pulso_amplitud=0.08,
            pulso_velocidad=3
        )

    def draw_instruccion_escribe(self):
        draw_breathing_background(
            self.screen,
            base_color=BACKGROUND_COLOR,
            tiempo=self.tiempo_animacion,
            intensidad=20,
            velocidad=1
        )
        update_and_draw_particles(self.particles, self.screen, dt=1/60)

        texto_instruccion = [
            "En braille separamos los números",
            "con el punto 3 para decimal y",
            "el punto 4 para miles.",
            "¡Ahora es tu turno!",
            "Te mostraremos un número,",
            "y tú deberás escribirlo en Braille.",
            "No olvides usar el prefijo de número.",
            "",
            "Toca 'Siguiente' para comenzar."
        ]
        draw_multiline_centered(self.screen, texto_instruccion, self.assets.fonts['small'], y_start=49, line_spacing=25)

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
        self.screen.fill(BACKGROUND_COLOR)
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['default'], y=21, color=BLANCO, x=85)

        # --- Dibujar los puntos Braille ---
        for i, (x, y) in enumerate(self.puntos):
            if (i + 1) in self.tocados_correctos:
                color = VERDE
            elif (i + 1) in self.tocados_incorrectos:
                color = ROJO
            else:
                color = BLANCO

            draw_circle_with_label(self.screen, (x, y), 30, str(i + 1), self.assets.fonts['default'], color=color)

        # --- Dibujar feedback si existe ---
        if self.mostrar_feedback:
            # Elegir color basado en el tipo de feedback
            if self.mostrar_feedback == "¡Correcto!":
                color_feedback = AMARILLO_PASTEL  # Verde
            elif self.mostrar_feedback == "No es este, prueba otro.":
                color_feedback = NARANJA  # Rojo anaranjado
            else:
                color_feedback = AMARILLO_PASTEL  # Por si en el futuro hay más tipos

            draw_text_centered(
                surface=self.screen,
                text=self.mostrar_feedback,
                font=self.assets.fonts['small'],
                y=276,
                color=color_feedback
            )

    def draw_traduce(self):
        self.screen.fill(BACKGROUND_COLOR)

        # --- Dibujar título arriba ---
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['default'], y=21, color=BLANCO, x=85)

        # Dibuja progreso
        draw_progress_text(
            surface=self.screen,
            font=self.assets.fonts['tiny'],
            current=self.total_intentos_traduce,
            total=10,
            x=274,
            y=56,
            color=AMARILLO_PASTEL
        )

        # --- Definir base X para la celda ---
        x_inicio_celda = self.back_icon_rect.right + 32  # 32px a la derecha del botón regresar

        # --- Coordenadas de los 6 puntos Braille ---
        puntos_posiciones = [
            (x_inicio_celda, 130),
            (x_inicio_celda, 200),
            (x_inicio_celda, 270),
            (x_inicio_celda + 80, 130),
            (x_inicio_celda + 80, 200),
            (x_inicio_celda + 80, 270)
        ]

        # --- Dibujar puntos Braille ---
        for i, (x, y) in enumerate(puntos_posiciones):
            punto_numero = i + 1
            color = VERDE if punto_numero in self.puntos_seleccionados else BLANCO
            draw_circle_with_label(self.screen, (x, y), 30, str(punto_numero), self.assets.fonts['default'], color=color)

        # --- Texto de número o feedback ---
        if not self.estado_validacion:
            texto_mostrar = self.numero_actual
            color_feedback = BLANCO
        else:
            texto_mostrar = self.mensaje_resultado

            # Definir el color según el mensaje de resultado
            if self.mensaje_resultado == "Correcto":
                color_feedback = VERDE  
            elif self.mensaje_resultado == "Incorrecto":
                color_feedback = NARANJA  
            elif self.mensaje_resultado == "Selecciona al menos un punto":
                color_feedback = AMARILLO_PASTEL 
            else:
                color_feedback = BLANCO  # Por si hay otros mensajes

        # --- Dibujar el mensaje ---
        draw_text_centered(
            surface=self.screen,
            text=texto_mostrar,
            font=self.assets.fonts['small'],
            y=148,
            color=color_feedback,
            x=274  # Colocarlo donde lo quieras
        )

        # --- Botón de Palomita ✔️ usando tu imagen ---
        self.palomita_rect = self.check_icon.get_rect(topright=(WIDTH - 10, HEIGHT - 70))
        self.screen.blit(self.check_icon, self.palomita_rect.topleft)

        # --- Dibujar sidebar y menús si están visibles ---
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

    def draw_escribe(self):
        self.screen.fill(BACKGROUND_COLOR)

        draw_text_centered(
            surface=self.screen,
            text=self.numero_actual_escribe,
            font=self.assets.fonts['default'],
            y=39,
            color=BLANCO
        )

        # --- Mostrar progreso ---
        draw_progress_text(
            surface=self.screen,
            font=self.assets.fonts['tiny'],
            current=self.total_intentos_escribe,
            total=10,
            x=334,
            y=30,
            color=AMARILLO_PASTEL
        )

        # --- 2. Mostrar "Respuesta" o "Correcto/Incorrecto" con color dinámico ---
        if self.estado_validacion_escribe:
            texto_respuesta = self.mensaje_resultado_escribe
            if self.mensaje_resultado_escribe == "Correcto":
                color_respuesta = VERDE
            else:
                color_respuesta = NARANJA
        else:
            #texto_respuesta = "Respuesta"
            texto_respuesta = self.mensaje_resultado_escribe
            color_respuesta = AMARILLO_PASTEL

        draw_text_centered(
            surface=self.screen,
            text=texto_respuesta,
            font=self.assets.fonts['tiny'],
            y=79,
            color=color_respuesta
        )

        # Dibujar las fichas
        fichas_orden = ["prefijo", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ",", "."]
        x_inicial = 20
        y_inicial = 110
        espacio_x = 65
        espacio_y = 63

        self.rects_fichas = {}

        for i, ficha in enumerate(fichas_orden):
            img = self.assets.fichas[ficha]
            fila = i // 7
            columna = i % 7
            x = x_inicial + columna * espacio_x
            y = y_inicial + fila * espacio_y

            rect = img.get_rect(topleft=(x, y))
            self.screen.blit(img, rect.topleft)

            self.rects_fichas[ficha] = rect
            # Dibujar borde si seleccionado
            #if ficha == self.ficha_seleccionada:
                #pygame.draw.rect(self.screen, AMARILLO_PASTEL, rect.inflate(6, 6), 3)

        # --- AGREGAR ESTA PARTE ---
        self.palomita_rect = self.check_icon.get_rect(topright=(WIDTH - 10, HEIGHT - 70))
        self.screen.blit(self.check_icon, self.palomita_rect.topleft)
        # --- FIN DE AGREGADO ---

    def draw_quiz(self):
        self.screen.fill(BACKGROUND_COLOR)
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['default'], y=21, color=BLANCO, x=85)

    def handle_event_escribe(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # --- Detectar clic en palomita ---
            if self.palomita_rect.collidepoint(pos):
                if not self.estado_validacion_escribe:
                    self.validar_respuesta_escribe()
                return

            # --- Detectar clic en fichas ---
            for ficha, rect in self.rects_fichas.items():
                if rect.collidepoint(pos):
                    self.ficha_seleccionada.append(ficha)
                    break


    def handle_event_quiz(self, event):
        # Por ahora no hacemos nada, pero evitamos errores
        pass

    def validar_traduccion(self):
        if not self.puntos_seleccionados:
            self.mensaje_resultado = "Selecciona al menos un punto"
        else:
            puntos_correctos = set(self.numeros_braille[self.numero_actual])
            if self.puntos_seleccionados == puntos_correctos:
                self.mensaje_resultado = "Correcto"
                self.aciertos_traduce += 1
            else:
                self.mensaje_resultado = "Incorrecto"

        self.total_intentos_traduce += 1
        self.estado_validacion = True
        self.esperando_nuevo_numero = True
        self.tiempo_validacion = 0
        self.puntos_seleccionados.clear()  # ← Resetear puntos seleccionados al validar

    def generar_nuevo_numero(self):
        self.numero_actual = random.choice(list(self.numeros_braille.keys()))
        self.puntos_seleccionados.clear()
        self.mensaje_resultado = ""
        self.estado_validacion = False
    
    def mostrar_popup_final_traduce(self):
        if self.aciertos_traduce >= 9:
            mensaje = "¡Excelente trabajo!"
        elif self.aciertos_traduce >= 7:
            mensaje = "¡Muy bien, sigue así!"
        else:
            mensaje = "¡Vamos a intentarlo de nuevo!"

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['small'],
            font_text=self.assets.fonts['tiny'],
            title=f"{mensaje}",
            message=f"Aciertos: {self.aciertos_traduce}/10",
            on_close=self.terminar_traduce,
            show_next=False
        )
        self.popup.show()

    def terminar_traduce(self):
        if self.aciertos_traduce >= 7:
            self.progress.mark_exercise_done("basico_1", "numeros", "Traduce números")
            self.current_index = 2  # Avanzar a Escribe un número
        else:
            self.current_index = 1  # Volver a "Traduce números"

        self.limpiar_estado_traduce()
        self.reset_state()

    def limpiar_estado_traduce(self):
        self.estado = "en_curso"
        self.popup = None
        self.tocados_correctos.clear()
        self.tocados_incorrectos.clear()
        self.mostrar_feedback = ""
        self.puntos_seleccionados.clear()
        self.mensaje_resultado = ""
        self.estado_validacion = False
        self.esperando_nuevo_numero = False
        self.tiempo_validacion = 0
        self.numero_actual = ""
        self.total_intentos_traduce = 0
        self.aciertos_traduce = 0

    def generar_nuevo_numero_escribe(self):
        # 1. Definir si es entero o decimal
        tipo = random.choice(["entero", "decimal"])

        if tipo == "entero":
            numero = random.randint(1, 99999)  # Por ejemplo 5483
            numero_str = f"{numero:,}"  # Formato con separadores de miles (ej: 5,483)
        else:
            numero_entero = random.randint(1, 999)  # Parte entera
            numero_decimal = random.randint(0, 99)  # Parte decimal
            numero_str = f"{numero_entero}.{numero_decimal:02d}"  # Ej: 25.07

        # 2. Validar que no pase de 8 caracteres
        while len(numero_str) > 8:
            tipo = random.choice(["entero", "decimal"])
            if tipo == "entero":
                numero = random.randint(1, 9999)
                numero_str = f"{numero:,}"
            else:
                numero_entero = random.randint(1, 99)
                numero_decimal = random.randint(0, 99)
                numero_str = f"{numero_entero}.{numero_decimal:02d}"

        # 3. Guardar número generado
        self.numero_actual_escribe = numero_str

        # 4. Separarlo en componentes (caracteres individuales)
        self.componentes_escribe = []

        # Siempre empezar agregando el prefijo primero
        self.componentes_escribe.append("prefijo")

        # Luego agregar los caracteres uno por uno
        for caracter in numero_str:
            if caracter.isdigit():
                self.componentes_escribe.append(caracter)
            elif caracter == ",":
                self.componentes_escribe.append(",")
            elif caracter == ".":
                self.componentes_escribe.append(".")

        # Reiniciar estado de respuesta
        self.ficha_seleccionada = []
        self.indice_actual = 0
        self.estado_validacion_escribe = False
        self.mensaje_resultado_escribe = ""
        self.esperando_nuevo_numero_escribe = False
        self.tiempo_validacion_escribe = 0

    def validar_respuesta_escribe(self):
        # Comparar lo que seleccionó el usuario con la respuesta correcta
        if self.ficha_seleccionada == self.componentes_escribe:
            self.mensaje_resultado_escribe = "Correcto"
            self.aciertos_escribe += 1
        else:
            self.mensaje_resultado_escribe = "Incorrecto"

        self.total_intentos_escribe += 1
        self.estado_validacion_escribe = True
        self.esperando_nuevo_numero_escribe = True
        self.tiempo_validacion_escribe = 0

        # Si quieres, puedes imprimir para debug:
        print(f"Esperado: {self.componentes_escribe}")
        print(f"Seleccionado: {self.ficha_seleccionada}")

    def mostrar_popup_final_escribe(self):
        if self.aciertos_escribe >= 9:
            mensaje = "¡Excelente trabajo!"
        elif self.aciertos_escribe >= 7:
            mensaje = "¡Muy bien, sigue practicando!"
        else:
            mensaje = "¡Vamos a intentarlo de nuevo!"

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['small'],
            font_text=self.assets.fonts['tiny'],
            title=mensaje,
            message=f"Aciertos: {self.aciertos_escribe}/10",
            on_close=self.terminar_escribe,
            show_next=False
        )
        self.popup.show()
    
    def terminar_escribe(self):
        if self.aciertos_escribe >= 7:
            self.progress.mark_exercise_done("basico_1", "numeros", "Escribe un número")
            self.mostrar_popup_seccion_completada()
        else:
            self.current_index = 2  # Repite Escribe un número
            self.reset_state()


    def mostrar_popup_seccion_completada(self):
        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title="¡Sección completada!",
            message="¡Felicidades, completaste la sección de Números!",
            on_close=lambda: "select_level",  # Para que regrese al menú
            show_next=False
        )
        self.popup.show()

    def switch_exercise(self, index):
        self.current_index = index
        self.reset_state()

    def next_exercise(self):
        if self.current_index < len(self.ejercicios) - 1:
            self.current_index += 1
            self.reset_state()
        else:
            self.mostrar_popup_seccion_completada()


    def reset_state(self):
        self.estado = "en_curso"
        self.popup = None
        self.tocados_correctos.clear()
        self.tocados_incorrectos.clear()
        self.mostrar_feedback = ""
        self.modo = "instruccion"

        if self.current_index == 1:
            self.generar_nuevo_numero()
        elif self.current_index == 2:
            self.generar_nuevo_numero_escribe()

            self.total_intentos_escribe = 0
            self.aciertos_escribe = 0
            self.ficha_seleccionada = []
            self.estado_validacion_escribe = False
            self.tiempo_validacion_escribe = 0
            self.esperando_nuevo_numero_escribe = False


        self.puntos_seleccionados.clear()
        self.mensaje_resultado = ""
        self.estado_validacion = False
        self.total_intentos_traduce = 0
        self.aciertos_traduce = 0
        self.esperando_nuevo_numero = False
        self.tiempo_validacion = 0

