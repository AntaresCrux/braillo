import pygame
import random
import json
from utils.settings import WIDTH, HEIGHT, ASSETS_PATHS
from utils.colors import BLANCO
from ui.ui_helpers import draw_text_centered, draw_circle_with_label
from ui.sidebar_menu import SidebarMenu
from ui.popup_message import PopupMessage

class LetraScene:
    def __init__(self, assets, progress):
        self.assets = assets
        self.progress = progress
        self.screen = pygame.display.get_surface()
        self.reset_drop_timer = None
        self.drop_ficha_activa = None
        self.mensaje_popup_acomoda = None
        self.popup_timer = None
        self.mensaje_popup_escribe = None
        self.popup_timer_escribe = None
        self.popup_timer_acomoda = None
        self.braille_map = self.cargar_braille_letras("assets/data/braille_letters.json")
        self.last_touch_time = pygame.time.get_ticks()
        self.inactividad_timeout = 5000  # 3 segundos de inactividad
        self.inactividad_detectada = False
        self.evaluar_button_escribe = pygame.Rect(130, 250, 150, 40)

        self.ejercicios = ["Escribe la letra", "Identifica la letra", "Acomoda la letra"]
        self.current_index = 0
        self.estado = "en_curso"
        self.escribe_aciertos = 0
        self.acomoda_intentos = 0
        self.max_intentos = 3
        self.identifica_intentos = 0
        self.max_identifica = 3

        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        self.sidebar = SidebarMenu(
            labels=["Escribe", "Identifica", "Acomoda"],
            font=self.assets.fonts['small'],
            width=240,
            height=HEIGHT
        )

        self.puntos = [
            (WIDTH - 145, 120), (WIDTH - 145, 180), (WIDTH - 145, 241),
            (WIDTH - 74, 120),  (WIDTH - 74, 180),  (WIDTH - 74, 241)
        ]

        self.objetivo_letra = ""
        self.objetivo_puntos = []
        self.seleccion_usuario = {}
        self.popup = None

        self.generar_letra()

    def cargar_braille_letras(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["letras"]

    def generar_letra(self):
        self.objetivo_letra = random.choice(list(self.braille_map.keys()))
        self.objetivo_puntos = self.braille_map[self.objetivo_letra]
        self.seleccion_usuario.clear()

    def handle_event(self, event):
        if self.popup:
            self.popup.handle_event(event)
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
            self.handle_event_escribe(event)
        elif self.current_index == 1:
            self.handle_event_identifica(event)
        elif self.current_index == 2:
             self.handle_event_acomoda(event)

    def handle_event_escribe(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.last_touch_time = pygame.time.get_ticks()
            self.inactividad_detectada = False
            # Si hace clic en el botón "Evaluar"
            if self.evaluar_button_escribe.collidepoint(event.pos):
                if not self.inactividad_detectada:
                    self.inactividad_detectada = True
                    self.evaluar_escribe_usuario()
                return
            for i, (x, y) in enumerate(self.puntos):
                if pygame.Rect(x - 20, y - 20, 40, 40).collidepoint(event.pos):
                    punto = i + 1
                    if punto in self.seleccion_usuario:
                        # Si ya estaba seleccionado, quitarlo (corregir)
                        del self.seleccion_usuario[punto]
                    else:
                        # Si no estaba seleccionado, marcarlo
                        correcto = punto in self.objetivo_puntos
                        self.seleccion_usuario[punto] = "correcto" if correcto else "incorrecto"


    def evaluar_escribe_usuario(self):
        seleccionados = set(self.seleccion_usuario.keys())
        correctos = set(self.objetivo_puntos)

        if seleccionados == correctos:
            mensaje = "Has escrito bien la letra."
            self.escribe_aciertos += 1
        else:
            mensaje = "No escribiste bien la letra."

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title="RESULTADO",
            message=mensaje,
            on_close=self.terminar_popup,
            on_next=None,
            show_next=False
        )
        self.popup.show()

    

    def update(self, dt):
        self.sidebar.update(dt)
        # Verificar inactividad en "Escribe la letra"
        if self.current_index == 0 and not self.popup and not self.inactividad_detectada:
            if pygame.time.get_ticks() - self.last_touch_time >= self.inactividad_timeout:
                self.inactividad_detectada = True
                self.evaluar_escribe_usuario()
        if self.reset_drop_timer and pygame.time.get_ticks() >= self.reset_drop_timer:
            self.reset_drop_timer = None

            if self.drop_ficha_activa:
                if self.drop_ficha_activa == self.objetivo_letra:
                    self.mostrar_popup("Identifica la letra")
                else:
                    # regresar ficha a su lugar original
                    original_x = 80 + self.opciones_fichas.index(self.drop_ficha_activa) * 75
                    original_y = HEIGHT - 100
                    self.ficha_posiciones[self.drop_ficha_activa]["pos"] = [original_x, original_y]
                    self.resultado_color = None
                    self.drop_ficha_activa = None

        if self.popup_timer_acomoda and pygame.time.get_ticks() >= self.popup_timer_acomoda:
            self.popup_timer_acomoda = None

            if self.mensaje_popup_acomoda:
                incorrectas = self.mensaje_popup_acomoda["incorrectas"]
                total = self.mensaje_popup_acomoda["total"]
                es_final = self.mensaje_popup_acomoda["final"]

                if es_final:
                    self.popup = PopupMessage(
                        self.screen,
                        font_title=self.assets.fonts['big'],
                        font_text=self.assets.fonts['small'],
                        title="¡BIEN HECHO!",
                        message="¡Sección completada!",
                        on_close=self.terminar_popup_final_acomoda,
                        on_next=None,
                        show_next=False  # ocultamos el botón
                    )
                else:
                    self.popup = PopupMessage(
                        self.screen,
                        font_title=self.assets.fonts['big'],
                        font_text=self.assets.fonts['small'],
                        title="RESULTADO",
                        message=f"Tuviste {incorrectas} malas de {total}",
                        on_close=self.terminar_popup,
                        on_next=None,
                        show_next=False
                    )
                self.popup.show()
                self.mensaje_popup_acomoda = None
        if self.mensaje_popup_escribe and self.popup_timer_escribe and pygame.time.get_ticks() >= self.popup_timer_escribe:
            self.popup_timer_escribe = None
            self.mostrar_popup(self.mensaje_popup_escribe)
            self.mensaje_popup_escribe = None

    def draw(self):
        self.screen.fill((13, 59, 102))
        draw_text_centered(self.screen, self.ejercicios[self.current_index], self.assets.fonts['default'], 30, color=BLANCO)

        if self.current_index == 0:
            self.draw_escribe()
        elif self.current_index == 1:
            self.draw_identifica()
        elif self.current_index == 2:
             self.draw_acomoda()

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
        ficha_image = pygame.image.load("assets/images/FichaBase.png").convert_alpha()
        ficha_image = pygame.transform.smoothscale(ficha_image, (160, 230))
        self.screen.blit(ficha_image, (WIDTH - 195, 70)) 
        # Render sombra (negra o gris oscura)
        sombra = self.assets.fonts['big'].render(self.objetivo_letra, True, (0, 0, 0))
        self.screen.blit(sombra, (92, HEIGHT // 2 - sombra.get_height() // 2 + 2))  # leve desplazamiento

        # Render texto principal (blanco)
        letra_grande = self.assets.fonts['big'].render(self.objetivo_letra, True, (255, 255, 255))
        self.screen.blit(letra_grande, (90, HEIGHT // 2 - letra_grande.get_height() // 2))
        # Mostrar progreso tipo "1 de 3"
        progreso_texto = f"{self.escribe_aciertos} / 3"
        progreso_render = self.assets.fonts['small'].render(progreso_texto, True, (244, 211, 94))
        progreso_x = 390
        progreso_y = 50  # altura superior

        self.screen.blit(progreso_render, (progreso_x, progreso_y))

        for i, (x, y) in enumerate(self.puntos):
            estado = self.seleccion_usuario.get(i + 1)
            color = (13, 59, 102)
            if estado == "correcto":
                color = (0, 200, 0)
            elif estado == "incorrecto":
                color = (200, 0, 0)

        draw_circle_with_label(self.screen, (x, y), 24, "", self.assets.fonts['big'], color=color)

        #draw_circle_with_label(self.screen, (x, y), 24, "", self.assets.fonts['giant'], color=color) mauricio
       # Mostrar barra de cuenta regresiva si está activo
        if not self.inactividad_detectada:
            elapsed = pygame.time.get_ticks() - self.last_touch_time
            progress = min(1.0, elapsed / self.inactividad_timeout)

            # Posición: entre letra y círculos (verticalmente)
            bar_width = 95
            bar_height = 17
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = HEIGHT // 2 - 90

            # Fondo de la barra
            pygame.draw.rect(self.screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), border_radius=10)

            # Color dinámico basado en progreso
            if progress < 0.5:
                bar_color = (0, 200, 0)  # Verde
            elif progress < 0.8:
                bar_color = (255, 215, 0)  # Amarillo
            else:
                bar_color = (249, 87, 56)  # Rojo

            # Barra de progreso
            pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=10)
        # Dibujar botón "Evaluar Ahora"
        pygame.draw.rect(self.screen, (249, 87, 56), self.evaluar_button_escribe, border_radius=10)
        texto_evaluar = self.assets.fonts['default'].render("Evaluar", True, (255, 255, 255))
        text_rect = texto_evaluar.get_rect(center=self.evaluar_button_escribe.center)
        self.screen.blit(texto_evaluar, text_rect)

    def iniciar_identifica(self):
        self.objetivo_letra = random.choice(list(self.braille_map.keys()))
        self.opciones_fichas = [self.objetivo_letra]
        letras_disponibles = list(self.braille_map.keys())
        letras_disponibles.remove(self.objetivo_letra)
        self.opciones_fichas += random.sample(letras_disponibles, 4)
        random.shuffle(self.opciones_fichas)

        self.ficha_imagenes = {
            letra: pygame.image.load(f"assets/images/{letra.lower()}.png").convert_alpha()
            for letra in self.opciones_fichas
        }

        self.ficha_posiciones = {}
        ficha_y = HEIGHT - 100
        for i, letra in enumerate(self.opciones_fichas):
            x = 80 + i * 75
            self.ficha_posiciones[letra] = {"pos": [x, ficha_y], "dragging": False, "offset": (0, 0)}

        self.drop_target_rect = pygame.Rect(WIDTH - 160, HEIGHT // 2 - 85, 120, 120)
        self.resultado_color = None
        self.ficha_correcta_colocada = False
        self.drop_ficha_activa = None
        self.reset_drop_timer = None

    def handle_event_identifica(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for letra, ficha in self.ficha_posiciones.items():
                rect = pygame.Rect(ficha["pos"][0], ficha["pos"][1], 80, 80)
                if rect.collidepoint(event.pos):
                    ficha["dragging"] = True
                    mouse_x, mouse_y = event.pos
                    offset_x = mouse_x - ficha["pos"][0]
                    offset_y = mouse_y - ficha["pos"][1]
                    ficha["offset"] = (offset_x, offset_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            for letra, ficha in self.ficha_posiciones.items():
                if ficha["dragging"]:
                    ficha["dragging"] = False
                    rect = pygame.Rect(ficha["pos"][0], ficha["pos"][1], 80, 80)
                    if self.drop_target_rect.colliderect(rect):
                        self.drop_ficha_activa = letra
                        if letra == self.objetivo_letra:
                            self.resultado_color = (0, 200, 0)
                            self.reset_drop_timer = pygame.time.get_ticks() + 1000  # esperar 1 seg
                        else:
                            self.resultado_color = (200, 0, 0)
                            self.reset_drop_timer = pygame.time.get_ticks() + 1000  # esperar 1 seg

        elif event.type == pygame.MOUSEMOTION:
            for ficha in self.ficha_posiciones.values():
                if ficha["dragging"]:
                    mouse_x, mouse_y = event.pos
                    offset_x, offset_y = ficha["offset"]
                    ficha["pos"][0] = mouse_x - offset_x
                    ficha["pos"][1] = mouse_y - offset_y

    def draw_identifica(self):
        sombra = self.assets.fonts['big'].render(self.objetivo_letra, True, (0, 0, 0))
        letra_surface = self.assets.fonts['big'].render(self.objetivo_letra, True, (255, 255, 255))
        centro_y = HEIGHT // 2 - 40
        self.screen.blit(sombra, (82, centro_y - sombra.get_height() // 2 + 2))
        self.screen.blit(letra_surface, (80, centro_y - letra_surface.get_height() // 2))
        

        if self.resultado_color:
            pygame.draw.rect(self.screen, self.resultado_color, self.drop_target_rect, border_radius=12)
        else:
            pygame.draw.rect(self.screen, (200, 200, 200), self.drop_target_rect, width=2, border_radius=12)

        for letra, ficha in self.ficha_posiciones.items():
            ficha_img = pygame.transform.scale(self.ficha_imagenes[letra], (55, 65))
            self.screen.blit(ficha_img, ficha["pos"])

    def iniciar_acomoda(self):
        self.palabras = self.cargar_palabras("assets/data/braille_letters.json")
        self.palabra_actual = random.choice(self.palabras).lower()
        self.letras_objetivo = list(self.palabra_actual)
        self.letras_colocadas = [None] * len(self.letras_objetivo)
        self.colores_slots = [None] * len(self.letras_objetivo)

        # Posiciones de los slots (centrados)
        total = len(self.letras_objetivo)
        start_x = WIDTH // 2 - (total * 70) // 2
        self.slots = []
        for i in range(total):
            slot_rect = pygame.Rect(start_x + i * 70, HEIGHT // 2 - 30, 60, 80)
            self.slots.append(slot_rect)

        # Mezclar letras
        letras_desordenadas = self.letras_objetivo[:]
        random.shuffle(letras_desordenadas)

        self.fichas = {}
        for i, letra in enumerate(letras_desordenadas):
            img = pygame.image.load(f"assets/images/{letra}.png").convert_alpha()
            pos = [80 + i * 75, HEIGHT - 100]
            self.fichas[letra + str(i)] = {
                "letra": letra,
                "imagen": pygame.transform.scale(img, (55, 65)),
                "pos": pos[:],
                "original_pos": pos.copy(),  # importante copiar por valor
                "dragging": False,
                "offset": (0, 0),
                "slot": None
            }

    def cargar_palabras(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["palabras"]

    def handle_event_acomoda(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for ficha_id, ficha in self.fichas.items():
                rect = pygame.Rect(ficha["pos"][0], ficha["pos"][1], 55, 65)
                if rect.collidepoint(event.pos):
                    ficha["dragging"] = True
                    mouse_x, mouse_y = event.pos
                    offset_x = mouse_x - ficha["pos"][0]
                    offset_y = mouse_y - ficha["pos"][1]
                    ficha["offset"] = (offset_x, offset_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            for ficha_id, ficha in self.fichas.items():
                if ficha["dragging"]:
                    ficha["dragging"] = False
                    # Si la ficha estaba en un slot y se soltó fuera → remover del slot
                    if ficha["slot"] is not None:
                        slot_idx = ficha["slot"]
                        if not self.slots[slot_idx].collidepoint(ficha["pos"]):
                            self.letras_colocadas[slot_idx] = None
                            self.colores_slots[slot_idx] = None
                            ficha["slot"] = None
                            self.popup_timer_acomoda = None

                    for i, slot in enumerate(self.slots):
                        if slot.collidepoint(ficha["pos"]):
                            # Si el slot ya tiene una ficha incorrecta, quitarla
                            if self.letras_colocadas[i] and self.colores_slots[i] == (200, 0, 0):
                                old_ficha_id = self.letras_colocadas[i]
                                old_ficha = self.fichas[old_ficha_id]
                                old_ficha["pos"] = old_ficha["original_pos"].copy()
                                old_ficha["slot"] = None
                            # Asignar nueva ficha
                            ficha["pos"] = [slot.x + 3, slot.y + 3]
                            self.letras_colocadas[i] = ficha_id
                            ficha["slot"] = i
                            break
                    else:
                        # Si no se soltó en un slot, regresar a posición original
                        ficha["pos"] = ficha["original_pos"].copy()
                        ficha["slot"] = None

            # Verificar si todos los slots están llenos
            if None not in self.letras_colocadas:
                print("Todos los slots están llenos, evaluando...")
                incorrectas = 0
                for i, ficha_id in enumerate(self.letras_colocadas):
                    letra_correcta = self.letras_objetivo[i]
                    letra_colocada = self.fichas[ficha_id]["letra"]
                    if letra_colocada == letra_correcta:
                        self.colores_slots[i] = (0, 200, 0)
                    else:
                        self.colores_slots[i] = (200, 0, 0)
                        incorrectas += 1

                self.acomoda_intentos += 1
                self.mensaje_popup_acomoda = {
                    "incorrectas": incorrectas,
                    "total": len(self.letras_objetivo),
                    "final": self.acomoda_intentos >= self.max_intentos
                }
                self.popup_timer_acomoda = pygame.time.get_ticks() + 5000


        elif event.type == pygame.MOUSEMOTION:
            for ficha in self.fichas.values():
                if ficha["dragging"]:
                    mouse_x, mouse_y = event.pos
                    offset_x, offset_y = ficha["offset"]
                    ficha["pos"][0] = mouse_x - offset_x
                    ficha["pos"][1] = mouse_y - offset_y

    def update_acomoda(self):
        if self.reset_drop_timer and pygame.time.get_ticks() >= self.reset_drop_timer:
            # Resetear solo las fichas incorrectas
            for i in range(len(self.letras_colocadas)):
                ficha_id = self.letras_colocadas[i]
                if ficha_id is None:
                    continue

                ficha = self.fichas[ficha_id]
                letra_correcta = self.letras_objetivo[i]
                letra_colocada = ficha["letra"]

                if letra_colocada != letra_correcta:
                    # Devolver ficha a posición original y limpiar el slot
                    ficha["pos"] = ficha["original_pos"].copy()
                    ficha["slot"] = None
                    self.letras_colocadas[i] = None
                    self.colores_slots[i] = None

            self.reset_drop_timer = None  # Reiniciar el temporizador

    def draw_acomoda(self):
        start_x = WIDTH // 2 - (len(self.letras_objetivo) * 70) // 2

        # Mostrar palabra modelo
        for i, letra in enumerate(self.letras_objetivo):
            text = self.assets.fonts['big'].render(letra.upper(), True, (255, 255, 255))
            self.screen.blit(text, (start_x + i * 70 + 5, 80))

        # Dibujar slots
        for i, slot in enumerate(self.slots):
            color = self.colores_slots[i] if self.colores_slots[i] else (250, 240, 200)
            pygame.draw.rect(self.screen, color, slot, border_radius=12)

        # Dibujar fichas colocadas en slots
        for i, ficha_id in enumerate(self.letras_colocadas):
            if ficha_id:
                ficha = self.fichas[ficha_id]
                self.screen.blit(ficha["imagen"], self.slots[i].topleft)

        # Dibujar fichas libres
        for ficha in self.fichas.values():
            if ficha["slot"] is None:
                self.screen.blit(ficha["imagen"], ficha["pos"])

    def mostrar_popup(self, ejercicio):
        self.estado = "completado"

        if ejercicio == "Escribe la letra":
            self.escribe_aciertos += 1
            if self.escribe_aciertos >= 3:
                self.current_index = 1
                self.estado = "en_curso"
                self.popup = None
                self.iniciar_identifica()
                self.escribe_aciertos = 0
                return
        elif ejercicio == "Identifica la letra":
            self.identifica_intentos += 1
            if self.identifica_intentos < self.max_identifica:
                self.estado = "en_curso"
                self.popup = None
                self.iniciar_identifica()
                return
            else:
                self.identifica_intentos = 0  # reset
                self.current_index = 2
                self.estado = "en_curso"
                self.popup = None
                self.iniciar_acomoda()
                return

        self.progress.mark_exercise_done("basico_1", "letras", ejercicio)

        mensaje = f"¡Correcto! Era la letra {self.objetivo_letra.upper()}" if ejercicio == "Identifica la letra" \
            else "Letra escrita correctamente"

        self.popup = PopupMessage(
            self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['small'],
            title="¡BIEN HECHO!",
            message=mensaje,
            on_close=self.terminar_popup,
            on_next=None,
            show_next=False
        )
        self.popup.show()

    def terminar_popup(self):
        self.popup = None
        self.estado = "en_curso"

        if self.current_index == 0:
            if self.escribe_aciertos >= 3:
                self.current_index = 1
                self.escribe_aciertos = 0
                self.iniciar_identifica()
            else:
                self.generar_letra()
                self.last_touch_time = pygame.time.get_ticks()
                self.inactividad_detectada = False

        elif self.current_index == 1:
            self.iniciar_identifica()
        elif self.current_index == 2:
            self.iniciar_acomoda()

    def terminar_popup_final_acomoda(self):
        self.popup = None
        self.estado = "completado"
        return "menu"

    def switch_exercise(self, index):
        self.current_index = index
        self.estado = "en_curso"
        self.seleccion_usuario.clear()
        self.popup = None

        if index == 0:
            self.generar_letra()
        elif index == 1:
            self.iniciar_identifica()
        elif index == 2:
            self.iniciar_acomoda()


if __name__ == "__main__":
    import pygame
    from src.core.assets_manager import AssetsManager
    from src.core.progress_manager import ProgressManager


    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # o usa WIDTH, HEIGHT
    assets = AssetsManager()
    progress = ProgressManager()
    scene = LetraScene(assets, progress)
    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = scene.handle_event(event)
                if result == "select_level":
                    running = False

        scene.update(dt)
        scene.draw()

    pygame.quit()