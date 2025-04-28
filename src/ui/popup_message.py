import pygame

class PopupMessage:
    def __init__(self, screen, font_title, font_text, title, message,
                 color_bg=(255, 245, 210), color_text=(0, 0, 0),
                 btn_texts=("Cerrar", "Siguiente"),
                 on_close=None, on_next=None,
                 show_next=True):  # ← NUEVO
        self.screen = screen
        self.font_title = font_title
        self.font_text = font_text
        self.title = title
        self.message = message
        self.color_bg = color_bg
        self.color_text = color_text
        self.on_close = on_close
        self.on_next = on_next
        self.show_next = show_next  # ← NUEVO

        self.visible = False
        self.width = 400
        self.height = 200
        self.rect = pygame.Rect(
            screen.get_width() // 2 - self.width // 2,
            screen.get_height() // 2 - self.height // 2,
            self.width, self.height
        )

        self.buttons = []
        self._create_buttons(btn_texts)

    def _create_buttons(self, texts):
        self.buttons = []

        btn_width = 130
        btn_height = 50
        spacing = 40
        total_width = btn_width * (2 if self.show_next else 1) + (spacing if self.show_next else 0)
        start_x = self.rect.centerx - total_width // 2
        y = self.rect.bottom - btn_height - 20

        # Botón de cerrar
        self.buttons.append({
            "text": texts[0],
            "rect": pygame.Rect(start_x, y, btn_width, btn_height),
            "action": self.on_close
        })

        # Botón de siguiente (si está habilitado)
        if self.show_next:
            self.buttons.append({
                "text": texts[1],
                "rect": pygame.Rect(start_x + btn_width + spacing, y, btn_width, btn_height),
                "action": self.on_next
            })

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn['rect'].collidepoint(event.pos):
                    if btn['action']:
                        btn['action']()
                    self.hide() # Ocultamos el popup después de hacer clic en un botón
                    return "close"  # ahora sí avisamos que se puede cerrar
                
    def draw(self):
        if not self.visible:
            return

        pygame.draw.rect(self.screen, self.color_bg, self.rect, border_radius=20)

        title_surf = self.font_title.render(self.title, True, self.color_text)
        msg_surf = self.font_text.render(self.message, True, self.color_text)

        self.screen.blit(title_surf, (self.rect.centerx - title_surf.get_width() // 2, self.rect.top + 30))
        self.screen.blit(msg_surf, (self.rect.centerx - msg_surf.get_width() // 2, self.rect.top + 80))

        for btn in self.buttons:
            pygame.draw.rect(self.screen, (249, 209, 84), btn['rect'], border_radius=20)
            text = self.font_text.render(btn['text'], True, (0, 0, 0))
            text_rect = text.get_rect(center=btn['rect'].center)
            self.screen.blit(text, text_rect)
