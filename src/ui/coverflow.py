import pygame
import math
from utils.settings import WIDTH, HEIGHT

# Constantes
MOUSE_CLICK_THRESHOLD = 5
DRAG_SENSITIVITY = 0.8
BUTTON_SELECT_RADIUS = 30
MAX_BUTTON_SIZE = 203
MIN_BUTTON_SIZE = 16
MAX_DISTANCE_FOR_SCALING = 400
CLICK_ANIM_DURATION = 0.25

class InputHandler:
    def __init__(self):
        self.dragging = False
        self.drag_start = (0, 0)

    def process(self, event, manager):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.dragging = True
            self.drag_start = event.pos

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.drag_start[0]
            dy = event.pos[1] - self.drag_start[1]
            if abs(dx) > abs(dy):  # Solo si predomina movimiento horizontal
                manager.scroll_pos -= dx * DRAG_SENSITIVITY
                manager.scroll_pos = max(0, min(manager.scroll_pos, manager.max_scroll))
                self.drag_start = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                movement = abs(event.pos[0] - self.drag_start[0])
                self.dragging = False
                manager.snap_to_nearest()
                if movement < MOUSE_CLICK_THRESHOLD:
                    return manager.handle_click(event.pos)
        return None

class CarruselManager:
    def __init__(self, buttons):
        self.buttons = buttons
        self.scroll_pos = 0.0
        self.target_pos = 0.0
        self.CENTER_X = WIDTH // 2
        self.BUTTON_SPACING = 165
        self.max_scroll = max(0, (len(buttons) - 1) * self.BUTTON_SPACING)

        self.clicked_index = None
        self.click_anim_time = 0

    def snap_to_nearest(self):
        self.target_pos = round(self.scroll_pos / self.BUTTON_SPACING) * self.BUTTON_SPACING
        self.target_pos = max(0, min(self.target_pos, self.max_scroll))

    def handle_click(self, mouse_pos):
        center_x = WIDTH // 2

        for i, btn_data in enumerate(self.buttons):
            rel_pos = (i * self.BUTTON_SPACING) - self.scroll_pos
            size = self.calculate_size(rel_pos)
            x = center_x + rel_pos - size // 2
            y = HEIGHT // 2 + 20 - size // 2

            # Solo el botón perfectamente alineado al centro se puede clicar
            center_btn_x = x + size // 2
            if abs(center_btn_x - center_x) < 20:  # Tolerancia pequeña
                btn_rect = pygame.Rect(x, y, size, size)
                if btn_rect.collidepoint(mouse_pos):
                    self.clicked_index = i
                    self.click_anim_time = 0
                    return i
        return None


    def calculate_size(self, rel_pos):
        distance = abs(rel_pos)
        factor = min(distance / MAX_DISTANCE_FOR_SCALING, 1.0)
        return int(MAX_BUTTON_SIZE - (MAX_BUTTON_SIZE - MIN_BUTTON_SIZE) * factor)

    def update(self, dt):
        speed = min(dt * 10, 0.1)
        self.scroll_pos += (self.target_pos - self.scroll_pos) * speed
        self.scroll_pos = max(0, min(self.scroll_pos, self.max_scroll))

        if self.clicked_index is not None:
            self.click_anim_time += dt
            if self.click_anim_time >= CLICK_ANIM_DURATION:
                self.clicked_index = None

class Renderer:
    def __init__(self, buttons, font):
        self.buttons = buttons
        self.font = font

    def draw(self, surface, scroll_pos, clicked_index, click_anim_time):
        center_x = WIDTH // 2

        for i, btn_data in enumerate(self.buttons):
            image, label = btn_data if isinstance(btn_data, tuple) else (btn_data, "")
            rel_pos = (i * 165) - scroll_pos
            distance = abs(rel_pos)

            factor = min(distance / MAX_DISTANCE_FOR_SCALING, 1.0)
            size = int(MAX_BUTTON_SIZE - (MAX_BUTTON_SIZE - MIN_BUTTON_SIZE) * factor)

            if clicked_index == i:
                pulse = math.sin((click_anim_time / CLICK_ANIM_DURATION) * math.pi)
                size += int(size * 0.1 * pulse)

            scaled_image = pygame.transform.smoothscale(image, (size, size))
            scaled_image.set_alpha(255 - int(155 * factor))

            x = center_x + rel_pos - size // 2
            y = HEIGHT // 2 + 20 - size // 2
            surface.blit(scaled_image, (x, y))

            center_btn_x = x + size // 2
            if abs(center_btn_x - center_x) < BUTTON_SELECT_RADIUS and label:
                text = self.font.render(label, True, (250, 240, 202))
                text_x = WIDTH // 2 - text.get_width() // 2
                text_y = y - text.get_height() - 10
                surface.blit(text, (text_x, text_y))

class CoverFlow:
    def __init__(self, buttons, font):
        self.input_handler = InputHandler()
        self.manager = CarruselManager(buttons)
        self.renderer = Renderer(buttons, font)
        self.ready_to_return_click = False


    def handle_event(self, event):
        result = self.input_handler.process(event, self.manager)
        return None  #

    def update(self, dt):
        self.manager.update(dt)
        if self.manager.clicked_index is not None:
            self.manager.click_anim_time += dt
            if self.manager.click_anim_time >= CLICK_ANIM_DURATION:
                self.ready_to_return_click = True

    def draw(self, surface):
        self.renderer.draw(surface, self.manager.scroll_pos, self.manager.clicked_index, self.manager.click_anim_time)

    def get_finished_click(self):
        if self.ready_to_return_click:
            result = self.manager.clicked_index
            self.manager.clicked_index = None
            self.manager.click_anim_time = 0
            self.ready_to_return_click = False
            return result
        return None