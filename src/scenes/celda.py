import pygame
import random
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BLANCO, AMARILLO_PASTEL, VERDE, NARANJA
from ui.ui_helpers import draw_text_centered, draw_circle_with_label
from ui.sidebar_menu import SidebarMenu
from ui.popup_message import PopupMessage

class CeldaScene:
    """
    Escena que representa la sección 'Celdas' del nivel básico de Braille.
    Incluye 3 ejercicios interactivos con mecánicas diferentes.
    """

    def __init__(self, assets, progress):
        """
        Inicializa todos los recursos necesarios para la escena:
        imágenes, fuente, menú lateral, lógica de progreso y variables de estado.
        """
        self.assets = assets
        self.progress = progress
        self.screen = pygame.display.get_surface()

        # Lista de nombres de ejercicios para navegación
        self.ejercicios = [
            "Explora la celda",
            "Toca el punto indicado",
            "Rellena la celda"
        ]
        self.current_index = 0    # Ejercicio activo
        self.estado = "en_curso"
        self.last_clicked = None  # Último punto tocado (solo para ejercicio 1)

        # Botón de menú lateral 
        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        # Botón de regresar a niveles
        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        # Menú lateral con nombres cortos de cada ejercicio
        self.sidebar = SidebarMenu(
            labels=["Explora", "Reconoce", "Prueba"],
            font=self.assets.fonts['small'],
            width=240,
            height=HEIGHT
        )

        # Coordenadas de los puntos Braille (se usan para los 3 ejercicios)
        self.puntos = [
            (180, 100), (180, 170), (180, 240),
            (300, 100), (300, 170), (300, 240)
        ]

        # Ejercicio 1: "Explora la celda"
        self.tocados = set()   # Puntos tocados (ejercicio 1)
        self.popup = None      # Popup activo (modal)

        # Ejercicio 2: "Toca el punto indicado"
        self.objetivo = 1
        self.aciertos = 0
        self.total_objetivos = 5
        self.mostrar_feedback = ""
        self.feedback_timer = 0         # Temporizador para mostrar el feedback
        self.feedback_mostrado = False  # Estado del feedback

        # Ejercicio 3: "Rellena la celda"
        self.patron_actual = []
        self.patron_aciertos = 0
        self.patron_mostrando = False
        self.seleccion_usuario = []
        #self.seleccion_usuario = set()
        self.temporizador_patron = 0
        self.tiempo_mostrar = 2000  # milisegundos para mostrar
        self.patron_index = 0  # índice actual del patrón que se está mostrando
        self.patron_timer = 0  # temporizador para cambiar de punto
        self.delay_entre_puntos = 600  # ms entre cada punto
        self.feedback_text = ""  # Texto actual a mostrar
        self.feedback_timer = 0  # Temporizador para feedback
        self.estado_juego = "esperando"  # Estados: 'esperando', 'mostrando', 'jugando', 'feedback'
        self.aciertos_total = 0
        self.errores_total = 0
        self.rondas_jugadas = 0
        self.max_rondas = 5

    def on_enter(self):
        """Se llama automáticamente al entrar a la escena para reiniciar el estado."""
        self.reset_state()


    def handle_event(self, event):
        """
        Controla todos los eventos del usuario:
        clics, navegación, toques en el menú y botones.
        """
        if self.popup:
            self.popup.handle_event(event)
            return

        # Si el menú está abierto, solo manejar eventos del menú
        if self.sidebar.visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_button_rect.collidepoint(event.pos):
                    self.sidebar.toggle()
                    return
                sidebar_index = self.sidebar.handle_event(event)
                if sidebar_index is not None:
                    self.switch_exercise(sidebar_index)
            return

        # Manejo de clics para botones principales
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_button_rect.collidepoint(event.pos):
                self.sidebar.toggle()
                return
            if self.back_icon_rect.collidepoint(event.pos):
                return "select_level"

        # Teclas para navegar entre ejercicios
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.next_exercise()
            elif event.key == pygame.K_LEFT:
                self.prev_exercise()

        # Redirigir eventos según el ejercicio actual
        if self.current_index == 0:
            self.handle_event_explora(event)
        elif self.current_index == 1:
            self.handle_event_reconoce(event)
        elif self.current_index == 2 and not self.patron_mostrando:
            self.handle_event_rellena(event)

    # Ejercicio 1: Explora la celda
    def handle_event_explora(self, event):
        """
        Guarda qué punto tocó el usuario.
        Se considera completado al tocar los 6 puntos.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (x, y) in enumerate(self.puntos):
                if pygame.Rect(x - 20, y - 20, 40, 40).collidepoint(event.pos):
                    self.last_clicked = i + 1
                    self.tocados.add(i + 1)

    # Ejercicio 2: Toca el punto indicado
    def handle_event_reconoce(self, event):
        """
        Muestra un número objetivo y evalúa si el punto tocado coincide.
        Se completan 5 rondas para finalizar el ejercicio.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.feedback_mostrado:
                return  # No aceptar clicks mientras mostramos feedback

            for i, (x, y) in enumerate(self.puntos):
                if pygame.Rect(x - 20, y - 20, 40, 40).collidepoint(event.pos):
                    if (i + 1) == self.objetivo:
                        self.aciertos += 1
                        self.mostrar_feedback = "¡Correcto!"
                    else:
                        self.mostrar_feedback = "Intenta otra vez"

                    # Siempre mostramos feedback
                    self.feedback_mostrado = True
                    self.feedback_timer = 1.0  # 1 segundo para mostrar

    # ===== Ejercicio 3: Rellena la celda =====
    def handle_event_rellena(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.estado_juego != "jugando":
                return  # Solo aceptar clics cuando toca jugar

            for i, (x, y) in enumerate(self.puntos):
                if pygame.Rect(x - 20, y - 20, 40, 40).collidepoint(event.pos):
                    if len(self.seleccion_usuario) < len(self.patron_actual):
                        self.seleccion_usuario.append(i + 1)

                    if len(self.seleccion_usuario) == len(self.patron_actual):
                        if self.seleccion_usuario == self.patron_actual:
                            self.feedback_text = "¡Correcto!"
                            self.feedback_resultado = "correcto"
                        else:
                            self.feedback_text = "Incorrecto"
                            self.feedback_resultado = "incorrecto"

                        self.estado_juego = "feedback"
                        self.feedback_timer = 0


    def mostrar_popup(self, ejercicio, seccion_completa=False):
        """
        Muestra un mensaje tipo modal. Cambia texto si ya estaba completado o si es repaso.
        También puede marcar el ejercicio como completado.
        """
        ya_completado = ejercicio in self.progress.get_completed("basico_1", "celdas")
        self.progress.mark_exercise_done("basico_1", "celdas", ejercicio)
        self.estado = "completado"

        title = "¡BIEN HECHO!" if not ya_completado else "¡Buen repaso!"
        message = "Ejercicio completado" if not seccion_completa else "Sección completada"

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title=title,
            message=message,
            on_close=lambda: setattr(self, "popup", None),
            on_next=None if seccion_completa else self.next_exercise,
            show_next=not seccion_completa
        )
        self.popup.show()

    def update(self, dt):
        self.sidebar.update(dt)

        # --- Ejercicio 2: Actualización de feedback ---
        if self.current_index == 1 and self.feedback_mostrado:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_mostrado = False
                if "Correcto" in self.mostrar_feedback:
                    if self.aciertos >= self.total_objetivos:
                        if self.estado != "completado":
                            self.mostrar_popup("Toca el punto correcto")
                    else:
                        self.objetivo = random.randint(1, 6)
                self.mostrar_feedback = ""

        # --- Ejercicio 3: Rellena la celda ---
        if self.current_index == 2:
            if self.estado_juego == "esperando":
                self.feedback_text = "Memoriza la secuencia..."
                self.feedback_timer += dt * 1000
                if self.feedback_timer >= 800:
                    self.estado_juego = "mostrando"
                    self.feedback_text = ""
                    self.patron_mostrando = True
                    self.patron_index = 0
                    self.patron_timer = 0

            elif self.estado_juego == "mostrando":
                self.patron_timer += dt * 1000
                if self.patron_timer >= self.delay_entre_puntos:
                    self.patron_timer = 0
                    self.patron_index += 1

                    if self.patron_index >= len(self.patron_actual):
                        self.estado_juego = "jugando"
                        self.patron_mostrando = False
                        self.patron_index = 0
                        self.seleccion_usuario.clear()
                        self.feedback_text = "Reproduce la secuencia"

            elif self.estado_juego == "feedback":
                self.feedback_timer += dt * 1000
                if self.feedback_timer >= 1500:
                    self.feedback_text = ""
                    if self.feedback_resultado == "correcto":
                        self.aciertos_total += 1
                    else:
                        self.errores_total += 1

                    self.rondas_jugadas += 1

                    if self.rondas_jugadas >= self.max_rondas:
                        self.estado_juego = "finalizado"
                        self.mostrar_resultado_final()
                        return  # salir de update para evitar bug del contador de aciertos
                    else:
                        self.generar_patron()
                        self.estado_juego = "esperando"
                        self.feedback_timer = 0


    def draw(self):
        """
        Dibuja toda la escena: fondo, botones, ejercicios y mensajes.
        """
        self.screen.fill((13, 59, 102))
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['default'], 30, color=BLANCO)

        if self.current_index == 0:
            self.draw_explora()
        elif self.current_index == 1:
            self.draw_reconoce()
        elif self.current_index == 2:
            self.draw_rellena()

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

    def draw_explora(self):
        for i, (x, y) in enumerate(self.puntos):
            draw_circle_with_label(self.screen, (x, y), 30, str(i + 1), self.assets.fonts['default']) #tamaño de los puntos

        if self.last_clicked is not None:
            draw_text_centered(self.screen, f"Tocaste el punto {self.last_clicked}", self.assets.fonts['small'], y=280, color=AMARILLO_PASTEL)

        if len(self.tocados) == 6 and self.estado != "completado":
            self.mostrar_popup("Explora la celda")

    def draw_reconoce(self):
        for i, (x, y) in enumerate(self.puntos):
            draw_circle_with_label(self.screen, (x, y), 30, str(i + 1), self.assets.fonts['default'])

        if not self.feedback_mostrado:
            # Solo mostrar el objetivo si no estamos mostrando feedback
            draw_text_centered(self.screen, f"Toca el punto {self.objetivo}", self.assets.fonts['small'], y=280, color=AMARILLO_PASTEL)
        else:
            # Mostrar el feedback durante la pausa
            color = VERDE if "Correcto" in self.mostrar_feedback else NARANJA
            draw_text_centered(self.screen, self.mostrar_feedback, self.assets.fonts['small'], y=280, color=color)

    def draw_rellena(self):
        """
        Dibuja los puntos de la celda en el ejercicio de memoria visual.
        Muestra uno a uno mientras se presenta el patrón.
        """
        for i, (x, y) in enumerate(self.puntos):
            punto_id = i + 1

            if self.patron_mostrando:
                if self.patron_index < len(self.patron_actual) and punto_id == self.patron_actual[self.patron_index]:
                    color = AMARILLO_PASTEL
                else:
                    color = BLANCO
            elif punto_id in self.seleccion_usuario:
                color = VERDE
            else:
                color = BLANCO

            draw_circle_with_label(self.screen, (x, y), 30, str(punto_id), self.assets.fonts['default'], color=color)

        # Mostrar número de ronda si estamos en el ejercicio 3
        if self.estado_juego in ("esperando", "mostrando", "jugando", "feedback"):
            texto_ronda = f"Ronda {self.rondas_jugadas + 1} de {self.max_rondas}"
            draw_text_centered(self.screen, texto_ronda, self.assets.fonts['tiny'], y=56, color=AMARILLO_PASTEL, x=320)

        #Mostrar texto de guía o feedback con color correcto (fuera del for)
        if self.feedback_text:
            if self.estado_juego == "feedback":
                color_texto = VERDE if self.feedback_resultado == "correcto" else NARANJA
            else:
                color_texto = BLANCO
            draw_text_centered(self.screen, self.feedback_text, self.assets.fonts['small'], y=280, color=color_texto)

        if not self.patron_actual:
            self.generar_patron()

    def generar_patron(self):
        """
        Crea un nuevo patrón aleatorio para el ejercicio de memoria visual.
        """
        self.patron_actual = random.sample(range(1, 7), 4)
        self.patron_mostrando = True
        self.temporizador_patron = self.tiempo_mostrar
        self.seleccion_usuario.clear()

    def mostrar_resultado_final(self):
        """
        Muestra popup final según el resultado tras 5 rondas.
        Si aciertos >= 4, marca como completado. Si no, se repite la sección.
        """
        aprobado = self.aciertos_total >= 4
        mensaje = f"Aciertos: {self.aciertos_total} de {self.max_rondas}"
        titulo = "¡BIEN HECHO!" if aprobado else "¡REINTENTALO!"
        completado = aprobado

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title=titulo,
            message=mensaje,
            on_close=self._cerrar_popup_si_aprobado if completado else self.reiniciar_ejercicio,
            on_next=None,
            show_next=False
        )

        self.popup.show()

        if completado:
            self.progress.mark_exercise_done("basico_1", "celdas", "Rellena la celda")
            self.estado = "completado"

    def _cerrar_popup_si_aprobado(self):
        self.popup = None
        self.estado = "completado"
        self.estado_juego = "finalizado"  # Asegura que no siga corriendo lógica de juego

    def switch_exercise(self, index):
        """
        Cambia al ejercicio seleccionado desde el menú lateral.
        """
        self.current_index = index
        self.reset_state()

    def next_exercise(self):
        """
        Avanza al siguiente ejercicio si existe.
        """
        if self.current_index < len(self.ejercicios) - 1:
            self.current_index += 1
            self.reset_state()

    def prev_exercise(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.reset_state()

    def reiniciar_ejercicio(self):
        self.aciertos_total = 0
        self.errores_total = 0
        self.rondas_jugadas = 0
        self.patron_actual = []
        self.seleccion_usuario.clear()
        self.estado_juego = "esperando"
        self.feedback_text = ""
        self.feedback_resultado = ""
        self.popup = None


    def reset_state(self):
        """
        Reinicia variables comunes entre ejercicios para evitar conflictos.
        """
        self.last_clicked = None
        self.tocados.clear()
        self.estado = "en_curso"
        self.popup = None
        self.objetivo = random.randint(1, 6)
        self.aciertos = 0
        self.mostrar_feedback = ""
        self.patron_actual = []
        self.patron_aciertos = 0
        self.seleccion_usuario.clear()
        self.patron_mostrando = False
        self.patron_index = 0  # índice actual del patrón que se está mostrando
        self.patron_timer = 0  # temporizador para cambiar de punto
        self.delay_entre_puntos = 600  # ms entre cada punto
        self.feedback_text = ""  # Texto actual a mostrar
        self.feedback_timer = 0  # Temporizador para feedback
        self.estado_juego = "esperando"  # Estados: 'esperando', 'mostrando', 'jugando', 'feedback'
        self.rondas_jugadas = 0
        self.max_rondas = 5

