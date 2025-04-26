import pygame
from PIL import Image, ImageSequence
import os
import sys
import math

# Inicialización
pygame.init()
WIDTH, HEIGHT = 480, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Braille App - Cover Flow")
clock = pygame.time.Clock()

# Configuración de colores
BG_COLOR = (254, 249, 255)  # Color de fondo base
FADE_COLOR = (0, 0, 0)      # Color para transiciones

# Clase para el efecto Cover Flow
class CoverFlow:
    def __init__(self, buttons):
        self.buttons = buttons
        self.scroll_pos = 0.0  # Posición de desplazamiento (float para suavizado)
        self.dragging = False
        self.drag_start_x = 0
        self.target_pos = 0
        self.BUTTON_SPACING = 150  # Espacio entre centros de botones
        self.CENTER_X = WIDTH // 2
        
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo
                self.dragging = True
                self.drag_start_x = event.pos[0]
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                # Snap al botón más cercano
                self.target_pos = round(self.scroll_pos / self.BUTTON_SPACING) * self.BUTTON_SPACING
            self.dragging = False
            
            # Detectar clic en botón
            mouse_pos = pygame.mouse.get_pos()
            for i, btn in enumerate(self.buttons):
                btn_center = self.CENTER_X + (i * self.BUTTON_SPACING - self.scroll_pos)
                if abs(mouse_pos[0] - btn_center) < 50:  # Margen de 50px
                    print(f"Botón {i+1} presionado!")
                    if i == len(self.buttons) - 1:  # Último botón (Salir)
                        return "salir"
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.drag_start_x
            self.scroll_pos -= dx * 0.8  # Factor de arrastre
            self.drag_start_x = event.pos[0]
            
        return None

    def update(self):
        # Suavizado automático al soltar
        if not self.dragging:
            self.scroll_pos += (self.target_pos - self.scroll_pos) * 0.1
            
    def draw(self, screen):
        for i, btn_data in enumerate(self.buttons):
            # Posición relativa al centro
            rel_pos = (i * self.BUTTON_SPACING) - self.scroll_pos
            distance = abs(rel_pos)
            
            # Transformaciones dinámicas
            scale = 1.0 - min(distance / 500, 0.4)  # Escala entre 60%-100%
            opacity = 255 - min(distance / 2, 155)   # Opacidad entre 100-255
            
            # Aplicar transformaciones
            btn = btn_data["image"]
            scaled_width = int(btn.get_width() * scale)
            scaled_height = int(btn.get_height() * scale)
            scaled_btn = pygame.transform.scale(btn, (scaled_width, scaled_height))
            scaled_btn.set_alpha(opacity)
            
            # Posición en curva (efecto 3D)
            btn_x = self.CENTER_X + rel_pos - scaled_width // 2
            btn_y = HEIGHT // 2 - scaled_height // 2 + (distance * 0.1)
            
            screen.blit(scaled_btn, (btn_x, btn_y))

# [El resto de tus funciones load_background_texture(), load_button_images(), load_gif() se mantienen igual]
def load_background_texture():
    try:
        texture = pygame.image.load("assets/images/tapiz.png").convert_alpha()
        # Escalar al tamaño de la pantalla manteniendo relación de aspecto
        texture = pygame.transform.smoothscale(texture, (WIDTH, HEIGHT))
        return texture
    except:
        print("¡Advertencia: No se encontró el tapiz! Usando fondo sólido.")
        return None

# Cargar imágenes de botones (tu código existente)
def load_button_images():
    buttons = []
    BUTTON_POSITIONS = [(80, 19), (80, 173), (274, 20), (274, 173)]
    for i, pos in enumerate(BUTTON_POSITIONS):
        try:
            img = pygame.image.load(f"assets/images/boton{i+1}.png").convert_alpha()
            btn_rect = img.get_rect(topleft=pos)
            buttons.append({
                "image": img,
                "rect": btn_rect,
                "action": "salir" if i == 3 else f"accion_{i+1}"
            })
        except:
            surf = pygame.Surface((96,96), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255,107,53), (0,0,96,96), border_radius=15)
            font = pygame.font.SysFont("Arial", 20)
            text = font.render(f"Btn {i+1}", True, (255,255,255))
            surf.blit(text, (48-text.get_width()//2, 48-text.get_height()//2))
            buttons.append({
                "image": surf,
                "rect": pygame.Rect(pos[0], pos[1], 96, 96),
                "action": "salir" if i == 3 else f"accion_{i+1}"
            })
    return buttons

# Cargar GIF (tu código existente)
def load_gif(path, target_size):
    try:
        gif = Image.open(path)
        frames = []
        original_size = gif.size
        ratio = min(target_size[0]/original_size[0], target_size[1]/original_size[1])
        new_size = (int(original_size[0]*ratio), int(original_size[1]*ratio))
        
        for frame in ImageSequence.Iterator(gif):
            duration = frame.info.get('duration', 100)
            frame = frame.convert("RGBA").resize(new_size, Image.LANCZOS)
            pygame_frame = pygame.image.fromstring(frame.tobytes(), new_size, "RGBA")
            frames.append((pygame_frame, max(10, duration)))
        
        return frames, new_size
    except Exception as e:
        print(f"Error al cargar GIF: {e}")
        return None, None

# Modificación en la carga de botones para Cover Flow
def load_coverflow_buttons():
    button_files = [
        "assets/images/boton1.png",
        "assets/images/boton2.png",
        "assets/images/boton3.png",
        "assets/images/boton4.png"
    ]
    buttons = []
    for i, file in enumerate(button_files):
        try:
            img = pygame.image.load(file).convert_alpha()
            buttons.append({
                "image": img,
                "action": "salir" if i == 3 else f"accion_{i+1}"
            })
        except:
            surf = pygame.Surface((96,96), pygame.SRCALPHA)
            color = (255,107,53) if i != 3 else (200,50,50)
            pygame.draw.rect(surf, color, (0,0,96,96), border_radius=15)
            font = pygame.font.SysFont("Arial", 20)
            text = font.render(f"Btn {i+1}", True, (255,255,255))
            surf.blit(text, (48-text.get_width()//2, 48-text.get_height()//2))
            buttons.append({
                "image": surf,
                "action": "salir" if i == 3 else f"accion_{i+1}"
            })
    return buttons

# Cargar recursos
background_texture = load_background_texture()
gif_frames, gif_size = load_gif("assets/media/logo-inicio.gif", (WIDTH, HEIGHT))
gif_pos = ((WIDTH-gif_size[0])//2, (HEIGHT-gif_size[1])//2) if gif_size else (0,0)
buttons_data = load_coverflow_buttons()
coverflow = CoverFlow(buttons_data)

# [Estados y controles se mantienen igual]
# Estados y controles (igual que antes)
STATE_FADE_IN, STATE_GIF, STATE_FADE_OUT, STATE_INTERFACE = 0, 1, 2, 3
current_state = STATE_FADE_IN if gif_frames else STATE_INTERFACE
current_frame = 0
last_frame_time = pygame.time.get_ticks()
fade_alpha = 255
fade_speed = 5
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill(FADE_COLOR)

# Bucle principal modificado
running = True
while running:
    current_time = pygame.time.get_ticks()
    
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        result = coverflow.handle_events(event)
        if result == "salir":
            running = False
        elif result:
            print(f"Ejecutando: {result}")

    # Lógica de estados
    if current_state == STATE_FADE_IN:
        fade_alpha = max(0, fade_alpha - fade_speed)
        if fade_alpha == 0:
            current_state = STATE_GIF
            last_frame_time = current_time
    
    elif current_state == STATE_GIF and gif_frames:
        frame, delay = gif_frames[current_frame]
        if current_time - last_frame_time > delay:
            current_frame = (current_frame + 1) % len(gif_frames)
            last_frame_time = current_time
            if current_frame == 0:
                current_state = STATE_FADE_OUT
    
    elif current_state == STATE_FADE_OUT:
        fade_alpha = min(255, fade_alpha + fade_speed)
        if fade_alpha == 255:
            current_state = STATE_INTERFACE

    # Renderizado
    screen.fill(BG_COLOR)
    if background_texture:
        screen.blit(background_texture, (0, 0))
    
    if current_state in [STATE_GIF, STATE_FADE_OUT] and gif_frames:
        screen.blit(gif_frames[current_frame][0], gif_pos)
    
    if current_state in [STATE_FADE_IN, STATE_FADE_OUT]:
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
    
    if current_state == STATE_INTERFACE:
        coverflow.update()
        coverflow.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
