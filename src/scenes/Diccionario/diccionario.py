import pygame
import sys
from src.utils import colors
from src.utils.settings import WIDTH, HEIGHT, ASSETS_PATHS



class diccionario:
    def __init__(self, screen_width=480, screen_height=320, scroll_speed=10):
        self.IMAGE_PATH = "assets/images/alfabeto.png"
        self.ALT_IMAGE_PATH = "assets/images/alfabeto.png"
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.SCROLL_SPEED = scroll_speed

        self.LEFT_MARGIN = 100
        self.TOP_MARGIN = 60
        self.IMAGE_SCALE = 1.0

        self.screen = pygame.display.get_surface()
        self.image = self.load_and_scale_image(self.IMAGE_PATH)
        self.alt_image = self.load_and_scale_image(self.ALT_IMAGE_PATH)

        self.active_image = self.image
        self.image_rect = self.active_image.get_rect()
        self.scroll_y = 0
        self.is_dragging = False
        self.last_y = 0

        self.clock = pygame.time.Clock()
        self.bg_color = colors.BACKGROUND_COLOR

        self.menu_button_rect = pygame.Rect(10, 10, 60, 60)
        self.menu_icon = pygame.image.load(ASSETS_PATHS['buttons']['menu']).convert_alpha()
        self.menu_icon = pygame.transform.smoothscale(self.menu_icon, (60, 60))

        self.back_icon = pygame.image.load(ASSETS_PATHS['buttons']['back']).convert_alpha()
        self.back_icon = pygame.transform.smoothscale(self.back_icon, (60, 60))
        self.back_icon_rect = self.back_icon.get_rect(topleft=(10, HEIGHT - 70))

        self.buttons = [
            {
                "label": "A-B",
                "image": "ficha_boton_a-z.png",
                "content_image": "alfabeto.png",
                "bg_color": (13, 59, 102),
                "rect": pygame.Rect(150, 10, 70, 40),
                "action": self.change_active_image
            },
            {
                "label": "MAY",
                "image": "ficha_boton_mayusculas.png",
                "content_image": "alfabeto_mayusculas.png",
                "bg_color": (250, 240, 202),
                "rect": pygame.Rect(230, 10, 70, 40),
                "action": self.change_active_image
            },
            {
                "label": "Ñ",
                "image": "ficha_boton_numeros.png",
                "content_image": "alfabeto_numeros.png",
                "bg_color": (249, 87, 56),
                "rect": pygame.Rect(310, 10, 70, 40),
                "action": self.change_active_image
            },
            {
                "label": ">",
                "image": "ficha_boton_signos.png",
                "content_image": "alfabeto_signos.png",
                "bg_color": (238, 150, 75),
                "rect": pygame.Rect(390, 10, 70, 40),
                "action": self.change_active_image
            },
        ]

        self.load_button_images()

    def load_and_scale_image(self, path):
        try:
            image = pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"No se pudo cargar la imagen: {e}")
            sys.exit()
        size = image.get_size()
        return pygame.transform.smoothscale(image, (int(size[0]*self.IMAGE_SCALE), int(size[1]*self.IMAGE_SCALE)))

    def load_button_images(self):
        for btn in self.buttons:
            if btn["image"]:
                try:
                    btn_img = pygame.image.load(f"assets/images/{btn['image']}").convert_alpha()
                    btn["img_surface"] = pygame.transform.scale(btn_img, (btn["rect"].width, btn["rect"].height))
                except:
                    print(f"⚠️ Imagen del botón '{btn['image']}' no encontrada.")
                    btn["img_surface"] = None
            else:
                btn["img_surface"] = None

    def change_active_image(self, image_filename):
        self.active_image = self.load_and_scale_image(f"assets/images/{image_filename}")
        self.image_rect = self.active_image.get_rect()
        self.scroll_y = 0

        for btn in self.buttons:
            if btn.get("content_image") == image_filename and "bg_color" in btn:
                self.bg_color = btn["bg_color"]
                break

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.last_y = event.pos[1]
            self.is_dragging = True
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    if "content_image" in btn:
                        btn["action"](btn["content_image"])
                    else:
                        btn["action"]()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            dy = self.last_y - event.pos[1]
            self.scroll_y += dy
            self.last_y = event.pos[1]

    def update(self, dt):
        self.scroll_y = max(0, min(self.scroll_y, self.image_rect.height - (self.SCREEN_HEIGHT - self.TOP_MARGIN)))

    def draw(self):
        self.screen.fill(self.bg_color)
        self.draw_buttons()
        self.screen.blit(
            self.active_image,
            (self.LEFT_MARGIN, self.TOP_MARGIN),
            area=pygame.Rect(0, self.scroll_y, self.SCREEN_WIDTH, self.SCREEN_HEIGHT - self.TOP_MARGIN)
        )
        self.clock.tick(30)
        pygame.display.flip()

    def draw_buttons(self):
        font = pygame.font.SysFont(None, 18)
        for btn in self.buttons:
            if btn["img_surface"]:
                self.screen.blit(btn["img_surface"], btn["rect"].topleft)
            else:
                pygame.draw.rect(self.screen, (200, 200, 200), btn["rect"])
                text = font.render(btn["label"], True, (0, 0, 0))
                self.screen.blit(text, (btn["rect"].x + 5, btn["rect"].y + 7))