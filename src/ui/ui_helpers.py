import pygame
import math
import random

class Particle:
    """
    Clase que representa una partícula flotante para el fondo animado.
    """

    def __init__(self, screen_width, screen_height):
        """
        Inicializa una partícula en una posición aleatoria dentro de la pantalla.

        Args:
            screen_width (int): Ancho de la pantalla.
            screen_height (int): Alto de la pantalla.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        """
        Reinicia la partícula en una nueva posición aleatoria en la parte inferior.
        """
        self.x = random.uniform(0, self.screen_width)
        self.y = random.uniform(self.screen_height, self.screen_height + 100)  # Aparecen de abajo
        self.radius = random.randint(2, 5)  # Tamaño pequeño
        self.speed_y = random.uniform(10, 30) / 100.0  # Velocidad lenta
        self.alpha = random.randint(50, 120)  # Transparencia baja

    def update(self, dt):
        """
        Actualiza la posición de la partícula.

        Args:
            dt (float): Delta time (tiempo entre frames).
        """
        self.y -= self.speed_y * dt * 100  # Movimiento hacia arriba

        # Si sale por arriba, se reinicia
        if self.y < -10:
            self.reset()

    def draw(self, surface):
        """
        Dibuja la partícula en la pantalla.

        Args:
            surface: Superficie de pygame donde se dibuja.
        """
        particle_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (255, 255, 255, self.alpha), (self.radius, self.radius), self.radius)
        surface.blit(particle_surface, (self.x - self.radius, self.y - self.radius))

def create_particles(amount, screen_width, screen_height):
    """
    Crea una lista de partículas.

    Args:
        amount (int): Número de partículas a crear.
        screen_width (int): Ancho de la pantalla.
        screen_height (int): Alto de la pantalla.

    Returns:
        list: Lista de objetos Particle.
    """
    return [Particle(screen_width, screen_height) for _ in range(amount)]

def update_and_draw_particles(particles, surface, dt):
    """
    Actualiza y dibuja todas las partículas.

    Args:
        particles (list): Lista de partículas.
        surface: Superficie de pygame donde se dibujan.
        dt (float): Delta time (tiempo entre frames).
    """
    for particle in particles:
        particle.update(dt)
        particle.draw(surface)

def draw_text_centered(surface, text, font, y, color, x=None):
    """
    Dibuja una línea de texto en la pantalla.

    Si no se especifica x, centra el texto automáticamente.

    Args:
        surface: Superficie de pygame donde se dibuja el texto.
        text (str): El texto a dibujar.
        font: Fuente pygame para renderizar el texto.
        y (int): Posición vertical (eje Y) donde dibujar el texto.
        x (int, optional): Posición horizontal (eje X). Si es None, se centra.
        color (tuple): Color del texto en formato RGB.
    """
    text_surface = font.render(text, True, color)
    
    if x is None:
        x = surface.get_width() // 2 - text_surface.get_width() // 2

    surface.blit(text_surface, (x, y))

def draw_multiline_centered(surface, text_lines, font, y_start, line_spacing=30, color=(255, 255, 255)):
    """
    Dibuja múltiples líneas de texto centradas horizontalmente en pantalla.

    Args:
        surface: Superficie de pygame donde se dibujan los textos.
        text_lines (list of str): Lista de líneas de texto a dibujar.
        font: Fuente pygame para renderizar los textos.
        y_start (int): Posición vertical inicial para la primera línea.
        line_spacing (int): Espacio vertical entre cada línea.
        color (tuple): Color del texto en formato RGB.
    """
    for i, line in enumerate(text_lines):
        y = y_start + i * line_spacing
        draw_text_centered(surface, line, font, y, color)

def draw_shadowed_box(surface, rect, color, border_radius=20, shadow_color=(0, 0, 0, 100)):
    """
    Dibuja un rectángulo de color con sombra detrás.

    Args:
        surface: Superficie de pygame donde se dibuja.
        rect: Rectángulo pygame.Rect donde dibujar.
        color (tuple): Color principal del rectángulo en RGB.
        border_radius (int): Radio de curvatura de las esquinas.
        shadow_color (tuple): Color de la sombra en formato RGBA.
    """
    sombra = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    sombra.fill(shadow_color)
    surface.blit(sombra, rect.topleft)
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)

def draw_circle_with_label(surface, center, radius, label, font, color=(255, 255, 255), label_color=(255, 255, 255)):
    """
    Dibuja un círculo con una etiqueta (texto) centrada dentro.

    Args:
        surface: Superficie de pygame donde se dibuja.
        center (tuple): Coordenadas (x, y) del centro del círculo.
        radius (int): Radio del círculo.
        label (str): Texto a mostrar dentro del círculo.
        font: Fuente pygame para renderizar el label.
        color (tuple): Color del círculo.
        label_color (tuple): Color del texto del label.
    """
    pygame.draw.circle(surface, color, center, radius)
    text = font.render(label, True, label_color)
    text_rect = text.get_rect(center=center)
    surface.blit(text, text_rect)

def draw_text_inside_rect(surface, text, font, rect, color=(0, 0, 0)):
    """
    Dibuja un texto centrado dentro de un rectángulo dado.

    Args:
        surface: Superficie de pygame donde se dibuja.
        text (str): Texto a renderizar.
        font: Fuente pygame para el texto.
        rect: Rectángulo pygame.Rect en el que centrar el texto.
        color (tuple): Color del texto en formato RGB.
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_pulsing_button(surface, image, center_position, tiempo, base_size, pulso_amplitud=0.05, pulso_velocidad=2):
    """
    Dibuja un botón que pulsa (se agranda y encoge suavemente) basado en el tiempo.

    Args:
        surface: Superficie de pygame donde se dibuja el botón.
        image: Imagen del botón (de tipo Surface).
        center_position (tuple): Coordenadas (x, y) del centro donde se dibujará el botón.
        tiempo (float): Tiempo acumulado en segundos (normalmente manejado en update()).
        base_size (tuple): Tamaño base (ancho, alto) del botón sin animación.
        pulso_amplitud (float): Factor de agrandamiento (por ejemplo 0.05 = 5% más grande).
        pulso_velocidad (float): Velocidad del pulso (frecuencia de oscilación).
    """
    # Calcula el factor de escala usando una función seno
    factor_pulso = 1 + pulso_amplitud * math.sin(tiempo * pulso_velocidad)

    # Escala la imagen
    ancho_escalado = int(base_size[0] * factor_pulso)
    alto_escalado = int(base_size[1] * factor_pulso)
    imagen_escalada = pygame.transform.smoothscale(image, (ancho_escalado, alto_escalado))

    # Dibuja la imagen centrada en la posición deseada
    rect = imagen_escalada.get_rect(center=center_position)
    surface.blit(imagen_escalada, rect.topleft)

def draw_breathing_background(surface, base_color, tiempo, intensidad=20, velocidad=1):
    """
    Dibuja un fondo que cambia suavemente su luminosidad, simulando un efecto de respiración.

    Args:
        surface: Superficie de pygame donde se dibuja el fondo.
        base_color (tuple): Color base del fondo (R, G, B).
        tiempo (float): Tiempo acumulado en segundos (normalmente manejado en update()).
        intensidad (int): Cuánto puede oscilar cada componente de color (ej. 20 unidades arriba o abajo).
        velocidad (float): Velocidad de la oscilación (frecuencia de respiración).
    """
    # Calcula un factor basado en el seno del tiempo
    offset = math.sin(tiempo * velocidad) * intensidad

    # Aplica el offset a cada componente del color base, limitándolo entre 0-255
    r = min(max(base_color[0] + offset, 0), 255)
    g = min(max(base_color[1] + offset, 0), 255)
    b = min(max(base_color[2] + offset, 0), 255)

    # Crea el color final
    color_final = (int(r), int(g), int(b))

    # Dibuja el fondo con el nuevo color
    surface.fill(color_final)

def draw_braille_cell(surface, puntos_activos, x, y, radio=7, separacion_horizontal=37, separacion_vertical=30, color_on=(255, 255, 255), color_off=(150, 150, 150)):
    """
    Dibuja una celda Braille (6 puntos organizados 2x3).
    
    Args:
        surface (pygame.Surface): Superficie donde dibujar.
        puntos_activos (list[int]): Lista de puntos encendidos (del 1 al 6).
        x (int): Posición X inicial de la celda.
        y (int): Posición Y inicial de la celda.
        radio (int): Radio de los puntos Braille.
        separacion_horizontal (int): Distancia entre las columnas.
        separacion_vertical (int): Distancia entre las filas.
        color_on (tuple): Color de los puntos encendidos.
        color_off (tuple): Color de los puntos apagados.
    """
    # Definimos las posiciones de cada punto
    posiciones = [
        (x, y),  # Punto 1
        (x, y + separacion_vertical),  # Punto 2
        (x, y + 2 * separacion_vertical),  # Punto 3
        (x + separacion_horizontal, y),  # Punto 4
        (x + separacion_horizontal, y + separacion_vertical),  # Punto 5
        (x + separacion_horizontal, y + 2 * separacion_vertical)  # Punto 6
    ]

    # Dibujamos los 6 puntos
    for idx, (px, py) in enumerate(posiciones):
        color = color_on if (idx + 1) in puntos_activos else color_off
        pygame.draw.circle(surface, color, (px, py), radio)

def draw_braille_word(surface, palabra, braille_data, x_start, y_start, max_width,
                      radio=10, separacion_horizontal=40, separacion_vertical=40, espacio_letra=20,
                      incluir_prefijo=False):
    """
    Dibuja una palabra en Braille, ajustando automáticamente filas si se acaba el espacio horizontal.

    Args:
        surface (pygame.Surface): Superficie donde dibujar.
        palabra (str): Palabra a dibujar.
        braille_data (dict): Diccionario de letras y sus puntos activos.
        x_start (int): Posición X inicial.
        y_start (int): Posición Y inicial.
        max_width (int): Ancho máximo antes de saltar a la siguiente fila.
        radio (int): Radio de los puntos Braille.
        separacion_horizontal (int): Separación entre columnas de puntos.
        separacion_vertical (int): Separación entre filas de puntos.
        espacio_letra (int): Espacio entre letras (entre celdas).
        incluir_prefijo (bool): Si True, dibuja primero el prefijo de mayúscula.
    """
    x_actual = x_start
    y_actual = y_start

    posiciones = [
        (0, 0),
        (0, separacion_vertical),
        (0, separacion_vertical * 2),
        (separacion_horizontal, 0),
        (separacion_horizontal, separacion_vertical),
        (separacion_horizontal, separacion_vertical * 2)
    ]

    # Si debe incluir prefijo (por ejemplo en siglas)
    if incluir_prefijo:
        if x_actual + 2 * separacion_horizontal > max_width:
            x_actual = x_start
            y_actual += separacion_vertical * 3 + espacio_letra

        for idx, (dx, dy) in enumerate(posiciones):
            punto = idx + 1
            color = (255, 255, 255) if punto in [4, 6] else (150, 150, 150)
            pygame.draw.circle(surface, color, (x_actual + dx, y_actual + dy), radio)

        x_actual += separacion_horizontal * 2 + espacio_letra

    for letra in palabra:
        if x_actual + 2 * separacion_horizontal > max_width:
            x_actual = x_start
            y_actual += separacion_vertical * 3 + espacio_letra

        puntos = braille_data.get(letra.lower(), [])
        for idx, (dx, dy) in enumerate(posiciones):
            punto = idx + 1
            color = (255, 255, 255) if punto in puntos else (150, 150, 150)
            pygame.draw.circle(surface, color, (x_actual + dx, y_actual + dy), radio)

        x_actual += separacion_horizontal * 2 + espacio_letra

def draw_progress_text(surface, font, current, total, x, y, color):
    """
    Dibuja un contador de progreso centrado.

    Parámetros:
    - surface: Superficie donde dibujar.
    - font: Fuente a usar.
    - current: Progreso actual.
    - total: Progreso total.
    - y: Posición vertical.
    - color: Color del texto (por defecto blanco).
    """
    texto = f"Progreso: {current}/{total}"
    render = font.render(texto, True, color)
    # Si no se da x, centrarlo
    if x is None:
        x = surface.get_width() // 2 - render.get_width() // 2
    surface.blit(render, (x, y))
