import pygame
from PIL import Image, ImageSequence
import sys

# Inicialización
pygame.init()
WIDTH, HEIGHT = 480, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Braille App - 4 Botones")
clock = pygame.time.Clock()

# Configuración de colores
BG_COLOR = (13, 59, 102)  # #0D3B66 (azul oscuro)
BUTTON_COLOR = (250, 240, 202)  # #FF6B35 (naranja)
BUTTON_TEXT_COLOR = (255, 255, 255)  # Texto blanco

# Posiciones y tamaño de los botones
BUTTON_SIZE = 96
BUTTON_POSITIONS = [
    (71, 30),    # Botón 1 - Superior izquierdo
    (71, 193),   # Botón 2 - Inferior izquierdo
    (314, 30),   # Botón 3 - Superior derecho
    (314, 193)   # Botón 4 - Inferior derecho
]
CORNER_RADIUS = 28  # Esquinas ligeramente redondeadas

# Función para cargar GIF (igual que antes)
def load_gif(path, target_size):
    try:
        gif = Image.open(path)
        frames = []
        original_size = gif.size
        ratio = min(target_size[0]/original_size[0], target_size[1]/original_size[1])
        new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
        
        for frame in ImageSequence.Iterator(gif):
            duration = frame.info.get('duration', 100)
            frame = frame.convert("RGBA").resize(new_size, Image.LANCZOS)
            pygame_frame = pygame.image.fromstring(frame.tobytes(), new_size, "RGBA")
            frames.append((pygame_frame, max(10, duration)))
        
        return frames, new_size
    except Exception as e:
        print(f"Error al cargar GIF: {e}")
        return None, None

# Cargar GIF
gif_frames, gif_size = load_gif("assets/media/intro_braillo.gif", (WIDTH, HEIGHT))
gif_pos = ((WIDTH - gif_size[0]) // 2, (HEIGHT - gif_size[1]) // 2) if gif_size else (0, 0)

# Estados y controles (igual que antes)
STATE_FADE_IN, STATE_GIF, STATE_FADE_OUT, STATE_INTERFACE = 0, 1, 2, 3
current_state = STATE_FADE_IN if gif_frames else STATE_INTERFACE
current_frame = 0
last_frame_time = pygame.time.get_ticks()
fade_alpha = 255
fade_speed = 5
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill((0, 0, 0))

# Textos para los botones (personalízalos)
BUTTON_TEXTS = ["Opción 1", "Opción 2", "Opción 3", "Salir"]

# Bucle principal
running = True
while running:
    current_time = pygame.time.get_ticks()
    
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if current_state == STATE_INTERFACE and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, (x, y) in enumerate(BUTTON_POSITIONS):
                button_rect = pygame.Rect(x, y, BUTTON_SIZE, BUTTON_SIZE)
                if button_rect.collidepoint(mouse_pos):
                    if i == 3:  # Si es el último botón (Salir)
                        running = False
                        print("Botón salir presionado, cerrando programa")  # Acción para cada botón
                    else:
                        print(f"Botón {i+1} presionado")  # Acción para cada botón

    # Lógica de estados (igual que antes)
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
    
    if current_state in [STATE_GIF, STATE_FADE_OUT] and gif_frames:
        screen.blit(gif_frames[current_frame][0], gif_pos)
    
    if current_state in [STATE_FADE_IN, STATE_FADE_OUT]:
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
    
    if current_state == STATE_INTERFACE:
        # Dibujar los 4 botones
        font = pygame.font.SysFont("Arial", 18, bold=True)
        for i, (x, y) in enumerate(BUTTON_POSITIONS):
            # Rectángulo del botón
            pygame.draw.rect(
                screen, 
                BUTTON_COLOR, 
                (x, y, BUTTON_SIZE, BUTTON_SIZE),
                border_radius=CORNER_RADIUS
            )
            
            # Texto centrado en el botón
            text = font.render(BUTTON_TEXTS[i], True, BUTTON_TEXT_COLOR)
            text_rect = text.get_rect(center=(x + BUTTON_SIZE//2, y + BUTTON_SIZE//2))
            screen.blit(text, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()