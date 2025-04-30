import pygame
import json
import random
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BACKGROUND_COLOR, BLANCO, VERDE, ROJO, NARANJA
from ui.ui_helpers import draw_text_centered, draw_circle_with_label, draw_multiline_centered, draw_pulsing_button, draw_breathing_background, create_particles, update_and_draw_particles
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
            "Memorama"
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
            labels=["Aprende", "Memorama"],
            font=self.assets.fonts['small'],
            width=240,
            height=HEIGHT
        )

        self.boton_siguiente_img = pygame.image.load(ASSETS_PATHS['buttons']['next']).convert_alpha()
        self.boton_siguiente_img = pygame.transform.smoothscale(self.boton_siguiente_img, (60, 60))
        self.boton_siguiente_rect = self.boton_siguiente_img.get_rect(topright=(WIDTH - 10, HEIGHT - 70))

        with open('assets/data/braille_letters.json', 'r', encoding='utf-8') as f:
            self.braille_data = json.load(f)
        with open('assets/data/nombres_siglas.json', 'r', encoding='utf-8') as f:
            self.data_nombres_siglas = json.load(f)

        self.letras_braille = self.braille_data["letras"]
        self.mayusculas_braille = self.braille_data["mayusculas"]
        self.prefijo_mayuscula = self.braille_data["prefijos"]["mayuscula"]

        # Ejercicio 1
        self.puntos = [(180, 100), (180, 170), (180, 240), (300, 100), (300, 170), (300, 240)]
        self.modo = "instruccion"
        self.tocados_correctos = set()
        self.tocados_incorrectos = set()
        self.mostrar_feedback = ""
        self.feedback_timer = 0
        self.delay_popup = False

        # Ejercicio 2
        self.fichas_memorama = []
        self.ficha_seleccionada = []
        self.grid_posiciones_memorama = []
        self.ficha_seleccionada = []  # lista de hasta 2 fichas
        self.tiempo_espera = 0        # timestamp para comparar
        self.bloquear_input = False   # bandera para evitar más clics
        self.feedback_memorama = ""

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

            if self.current_index == 0:
                if self.modo == "instruccion":
                    if self.boton_siguiente_rect.collidepoint(event.pos):
                        self.modo = "interactivo"
                else:
                    self.handle_event_aprende(event)
            elif self.current_index == 1:
                self.handle_event_memorama(event)

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
                        self.feedback_timer = pygame.time.get_ticks()

            if {4, 6}.issubset(self.tocados_correctos):
                self.delay_popup = True
                self.feedback_timer = pygame.time.get_ticks()

    def handle_event_memorama(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.bloquear_input:
            for idx, ficha in enumerate(self.fichas_memorama):
                if ficha["revelada"] or ficha["emparejada"]:
                    continue
                x, y = self.grid_posiciones_memorama[idx]
                rect = pygame.Rect(x, y, 110, 110)
                if rect.collidepoint(event.pos):
                    ficha["revelada"] = True
                    self.ficha_seleccionada.append(ficha)
                    break

            if len(self.ficha_seleccionada) == 2:
                self.bloquear_input = True
                self.tiempo_espera = pygame.time.get_ticks()


    def mostrar_modal_prefijo(self):
        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title="¡BIEN HECHO!",
            message="Los puntos 4 y 6 crean el prefijo.",
            on_close=lambda: (self.progress.mark_exercise_done("basico_1", "mayusculas", "Aprende el prefijo"), self.next_exercise()),
            show_next=False
        )
        self.popup.show()
        self.estado = "completado"

    def update(self, dt):
        self.sidebar.update(dt)
        self.tiempo_animacion += dt

        now = pygame.time.get_ticks()

        if self.delay_popup and now - self.feedback_timer > 800:
            self.delay_popup = False
            self.mostrar_modal_prefijo()

        if self.tocados_incorrectos and now - self.feedback_timer > 1000:
            self.tocados_incorrectos.clear()
            self.mostrar_feedback = ""
        
        # Verificación después de mostrar 2 fichas
        if self.bloquear_input and len(self.ficha_seleccionada) == 2:
            if pygame.time.get_ticks() - self.tiempo_espera >= 1000:
                f1, f2 = self.ficha_seleccionada
                if f1["valor"] == f2["valor"] and f1["braille"] != f2["braille"]:
                    f1["emparejada"] = True
                    f2["emparejada"] = True
                    self.feedback_memorama = "¡Bien hecho! Son pareja."
                else:
                    f1["revelada"] = False
                    f2["revelada"] = False
                    self.feedback_memorama = "Ups... no son pareja"

                self.ficha_seleccionada.clear()
                self.bloquear_input = False
                self.feedback_timer = pygame.time.get_ticks()

        if self.feedback_memorama and pygame.time.get_ticks() - self.feedback_timer > 1500:
            self.feedback_memorama = ""

        # Verificar si ya se completaron todas las parejas
        if (
            self.estado == "en_curso" 
            and self.current_index == 1  # verifica que estés en el ejercicio 1
            and self.fichas_memorama      # solo si hay fichas generadas
            and all(f["emparejada"] for f in self.fichas_memorama)
        ):
            self.estado = "completado"
            self.popup = PopupMessage(
                self.screen,
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['small'],
                title="¡Buen trabajo!",
                message="Completaste el memorama.",
                on_close=lambda: self.progress.mark_exercise_done("basico_1", "mayusculas", "Memorama"),
                show_next=False
            )
            self.popup.show()


    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['default'], 22, color=BLANCO)

        if self.current_index == 0:
            if self.modo == "instruccion":
                self.draw_instruccion()
            else:
                self.draw_aprende()
        elif self.current_index == 1:
            self.draw_memorama()

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

    def draw_aprende(self):
        for i, (x, y) in enumerate(self.puntos):
            if (i + 1) in self.tocados_correctos:
                color = VERDE
            elif (i + 1) in self.tocados_incorrectos:
                color = ROJO
            else:
                color = BLANCO

            draw_circle_with_label(self.screen, (x, y), 30, str(i + 1), self.assets.fonts['default'], color=color)

        if self.mostrar_feedback:
            color_texto = VERDE if self.mostrar_feedback == "¡Correcto!" else NARANJA
            draw_text_centered(self.screen, self.mostrar_feedback, self.assets.fonts['small'], HEIGHT - 40, color=color_texto)

    def draw_memorama(self):
        for idx, ficha in enumerate(self.fichas_memorama):
            x, y = self.grid_posiciones_memorama[idx]
            if ficha["revelada"] or ficha["emparejada"]:
                imagen = self.assets.memorama[ficha["id"]]
            else:
                imagen = self.assets.memorama["oculta"]

            rect = imagen.get_rect(topleft=(x, y))
            self.screen.blit(imagen, rect)

        if self.feedback_memorama:
            draw_text_centered(
                self.screen,
                self.feedback_memorama,
                self.assets.fonts['small'],
                HEIGHT - 30,
                color=VERDE if "Bien" in self.feedback_memorama else NARANJA
            )

    def switch_exercise(self, index):
        self.current_index = index
        self.reset_state()

    def next_exercise(self):
        if self.current_index < len(self.ejercicios) - 1:
            self.current_index += 1
            self.reset_state()

    def reset_state(self):
        self.estado = "en_curso"
        self.popup = None
        self.tocados_correctos.clear()
        self.tocados_incorrectos.clear()
        self.mostrar_feedback = ""
        self.modo = "instruccion"
        self.feedback_timer = 0
        self.delay_popup = False
        self.ficha_seleccionada = []
        self.tiempo_espera = 0
        self.bloquear_input = False

        # limpiar las fichas si no estás en el ejercicio 1
        if self.current_index != 1:
            self.fichas_memorama = []

        # generar fichas solo si esta en el memorama
        if self.current_index == 1:
            self.fichas_memorama = self.generar_memorama()
            self.grid_posiciones_memorama = self._generar_posiciones_memorama()


    def generar_memorama(self):
        letras = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
        banco_pares = [{"valor": letra, "tipo": "letra"} for letra in letras]
        banco_pares.append({"valor": "prefijo", "tipo": "prefijo"})

        pares_seleccionados = random.sample(banco_pares, 4)

        fichas = []
        for par in pares_seleccionados:
            fichas.append({
                "id": f"{par['valor']}_texto",
                "tipo": par["tipo"],
                "valor": par["valor"],
                "braille": False,
                "revelada": False,
                "emparejada": False
            })
            fichas.append({
                "id": f"{par['valor']}_braille",
                "tipo": par["tipo"],
                "valor": par["valor"],
                "braille": True,
                "revelada": False,
                "emparejada": False
            })

        random.shuffle(fichas)
        return fichas

    def _generar_posiciones_memorama(self):
        columnas = 4
        filas = 2
        ancho_ficha = 100   
        alto_ficha = 100    
        margen_x = 8        
        margen_y = 8        

        total_alto = filas * alto_ficha + (filas - 1) * margen_y

        inicio_x = 60
        inicio_y = (HEIGHT - total_alto) // 2

        posiciones = []
        for fila in range(filas):
            for col in range(columnas):
                x = inicio_x + col * (ancho_ficha + margen_x)
                y = inicio_y + fila * (alto_ficha + margen_y)
                posiciones.append((x, y))
        return posiciones


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
