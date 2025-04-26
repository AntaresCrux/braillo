import pygame
import math
from utils.settings import WIDTH, HEIGHT

class CoverFlow:
    def __init__(self, buttons, font):
        self.buttons = buttons  # List of (image, label) tuples
        self.font = font
        self.scroll_pos = 0.0
        self.target_pos = 0.0
        self.dragging = False
        self.drag_start_x = 0

        self.BUTTON_SPACING = 165
        self.CENTER_X = WIDTH // 2
        self.max_scroll = max(0, (len(self.buttons) - 1) * self.BUTTON_SPACING)

        # Animación al hacer clic
        self.clicked_index = None
        self.click_anim_time = 0
        self.click_anim_duration = 0.25  # segundos

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.dragging = True
            self.drag_start_x = event.pos[0]

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._handle_drag(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                movement = abs(event.pos[0] - self.drag_start_x)
                self.dragging = False
                self._snap_to_nearest()

                if movement < 5:  # Es clic real
                    return self._handle_button_click(event.pos)
        return None

    def _handle_drag(self, pos):
        dx = pos[0] - self.drag_start_x
        if abs(dx) > 5:
            self.scroll_pos -= dx * 0.8
            self.scroll_pos = max(0, min(self.scroll_pos, self.max_scroll))
            self.drag_start_x = pos[0]

    def _snap_to_nearest(self):
        self.target_pos = round(self.scroll_pos / self.BUTTON_SPACING) * self.BUTTON_SPACING
        self.target_pos = max(0, min(self.target_pos, self.max_scroll))

    def _handle_button_click(self, mouse_pos):
        self._snap_to_nearest()
        for i in range(len(self.buttons)):
            center_x = self.CENTER_X + (i * self.BUTTON_SPACING - self.scroll_pos)
            if abs(mouse_pos[0] - center_x) < 30:
                self.clicked_index = i
                self.click_anim_time = 0
                return i
        return None

    def update(self, dt):
        if not self.dragging:
            speed = min(dt * 10, 0.1)
            self.scroll_pos += (self.target_pos - self.scroll_pos) * speed
            self.scroll_pos = max(0, min(self.scroll_pos, self.max_scroll))

        if self.clicked_index is not None:
            self.click_anim_time += dt
            if self.click_anim_time >= self.click_anim_duration:
                self.clicked_index = None

    def draw(self, surface):
        for i, btn_data in enumerate(self.buttons):
            image, label = btn_data if isinstance(btn_data, tuple) else (btn_data, "")
            self._draw_button(surface, image, label, i)

    def _draw_button(self, surface, image, label, index):
        rel_pos = (index * self.BUTTON_SPACING) - self.scroll_pos
        distance = abs(rel_pos)

        max_size, min_size = 203, 16
        max_distance = 400
        factor = min(distance / max_distance, 1.0)
        size = int(max_size - (max_size - min_size) * factor)

        # Animación al hacer clic
        if self.clicked_index == index:
            pulse = math.sin((self.click_anim_time / self.click_anim_duration) * math.pi)
            size += int(size * 0.1 * pulse)

        scaled_image = pygame.transform.smoothscale(image, (size, size))
        scaled_image.set_alpha(255 - int(155 * factor))

        x = self.CENTER_X + rel_pos - size // 2
        y = HEIGHT // 2 + 20 - size // 2

        surface.blit(scaled_image, (x, y))

        center_btn_x = x + size // 2
        if abs(center_btn_x - self.CENTER_X) < 30 and label:
            text = self.font.render(label, True, (250, 240, 202))
            text_x = WIDTH // 2 - text.get_width() // 2
            text_y = y - text.get_height() - 10
            surface.blit(text, (text_x, text_y))