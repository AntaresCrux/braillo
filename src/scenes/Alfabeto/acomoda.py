# src/scenes/Alfabeto/acomoda.py
import pygame
import random
import json
from ui.popup_message import PopupMessage
from utils.settings import WIDTH, HEIGHT

class AcomodaLetra:
    def __init__(self, assets, json_path, on_completo_callback):
        self.assets = assets
        self.on_completo_callback = on_completo_callback
        self.palabras = self.cargar_palabras(json_path)
        self.intentos = 0
        self.max_intentos = 3
        self.popup = None
        self.popup_timer = None
        self.reset_drop_timer = None
        self.iniciar_nueva_palabra()

    def cargar_palabras(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["palabras"]

    def iniciar_nueva_palabra(self):
        self.popup = None
        self.popup_timer = None
        self.reset_drop_timer = None
        self.palabra_actual = random.choice(self.palabras).lower()
        self.letras_objetivo = list(self.palabra_actual)
        self.letras_colocadas = [None] * len(self.letras_objetivo)
        self.colores_slots = [None] * len(self.letras_objetivo)

        total = len(self.letras_objetivo)
        start_x = WIDTH // 2 - (total * 70) // 2
        self.slots = [pygame.Rect(start_x + i * 70, HEIGHT // 2 - 30, 60, 80) for i in range(total)]

        desordenadas = self.letras_objetivo[:]
        random.shuffle(desordenadas)

        self.fichas = {}
        for i, letra in enumerate(desordenadas):
            img = pygame.image.load(f"assets/images/{letra}.png").convert_alpha()
            pos = [80 + i * 75, HEIGHT - 100]
            self.fichas[letra + str(i)] = {
                "letra": letra,
                "imagen": pygame.transform.scale(img, (55, 65)),
                "pos": pos[:],
                "original_pos": pos[:],
                "dragging": False,
                "offset": (0, 0),
                "slot": None
            }
        for ficha in self.fichas.values():
            ficha["pos"] = ficha["original_pos"][:]
            ficha["slot"] = None
            ficha["dragging"] = False
            ficha["offset"] = (0, 0)

    def handle_event(self, event):
        if self.popup:
            self.popup.handle_event(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            for fid, ficha in self.fichas.items():
                rect = pygame.Rect(ficha["pos"][0], ficha["pos"][1], 55, 65)
                if rect.collidepoint(event.pos):
                    ficha["dragging"] = True
                    ox = event.pos[0] - ficha["pos"][0]
                    oy = event.pos[1] - ficha["pos"][1]
                    ficha["offset"] = (ox, oy)

        elif event.type == pygame.MOUSEMOTION:
            for ficha in self.fichas.values():
                if ficha["dragging"]:
                    mx, my = event.pos
                    ox, oy = ficha["offset"]
                    ficha["pos"][0] = mx - ox
                    ficha["pos"][1] = my - oy

        elif event.type == pygame.MOUSEBUTTONUP:
            for fid, ficha in self.fichas.items():
                if ficha["dragging"]:
                    ficha["dragging"] = False
                    # Si estaba en un slot pero se soltó fuera
                    if ficha["slot"] is not None:
                        idx = ficha["slot"]
                        if not self.slots[idx].collidepoint(ficha["pos"]):
                            self.letras_colocadas[idx] = None
                            self.colores_slots[idx] = None
                            ficha["slot"] = None
                            self.popup_timer = None

                    for i, slot in enumerate(self.slots):
                        if slot.collidepoint(ficha["pos"]):
                            # Si hay ficha incorrecta, reemplazar
                            if self.letras_colocadas[i] and self.colores_slots[i] == (200, 0, 0):
                                old_id = self.letras_colocadas[i]
                                old = self.fichas[old_id]
                                old["pos"] = old["original_pos"][:]
                                old["slot"] = None

                            ficha["pos"] = [slot.x + 3, slot.y + 3]
                            ficha["slot"] = i
                            self.letras_colocadas[i] = fid
                            break
                    else:
                        ficha["pos"] = ficha["original_pos"][:]
                        ficha["slot"] = None

            if None not in self.letras_colocadas:
                incorrectas = 0
                for i, fid in enumerate(self.letras_colocadas):
                    colocada = self.fichas[fid]["letra"]
                    correcta = self.letras_objetivo[i]
                    if colocada == correcta:
                        self.colores_slots[i] = (0, 200, 0)
                    else:
                        self.colores_slots[i] = (200, 0, 0)
                        incorrectas += 1

                self.intentos += 1
                self.popup_data = {
                    "incorrectas": incorrectas,
                    "total": len(self.letras_objetivo)
                }
                self.popup_timer = pygame.time.get_ticks() + 2000  # esperar 2s

    def update(self, dt):
        if self.popup_timer and pygame.time.get_ticks() >= self.popup_timer:
            self.popup_timer = None
            self.mostrar_resultado()

    def mostrar_resultado(self):
        data = self.popup_data
        mensaje = f"Tuviste {data['incorrectas']} malas de {data['total']}"

        if self.intentos >= self.max_intentos:
            self.popup = PopupMessage(
                pygame.display.get_surface(),
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['small'],
                title="¡Completado!",
                message="Terminaste los ejercicios de acomodar",
                on_close=self.on_completo_callback,
                on_next=None,
                show_next=False
            )
        else:
            self.popup = PopupMessage(
                pygame.display.get_surface(),
                font_title=self.assets.fonts['big'],
                font_text=self.assets.fonts['small'],
                title="RESULTADO",
                message=mensaje,
                on_close=self.iniciar_nueva_palabra,
                on_next=None,
                show_next=False
            )
        self.popup.show()

    def draw(self, screen):
        start_x = WIDTH // 2 - (len(self.letras_objetivo) * 70) // 2

        # palabra modelo
        for i, letra in enumerate(self.letras_objetivo):
            txt = self.assets.fonts['big'].render(letra.upper(), True, (255, 255, 255))
            screen.blit(txt, (start_x + i * 70 + 5, 80))

        # slots
        for i, slot in enumerate(self.slots):
            color = self.colores_slots[i] if self.colores_slots[i] else (240, 230, 180)
            pygame.draw.rect(screen, color, slot, border_radius=12)

        # fichas colocadas
        for i, fid in enumerate(self.letras_colocadas):
            if fid:
                ficha = self.fichas[fid]
                screen.blit(ficha["imagen"], self.slots[i].topleft)

        # fichas libres
        for ficha in self.fichas.values():
            if ficha["slot"] is None:
                screen.blit(ficha["imagen"], ficha["pos"])

        if self.popup:
            self.popup.draw()