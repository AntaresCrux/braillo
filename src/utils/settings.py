# Constantes de juego: FPS, tamaño de pantalla, etc.
import pygame

# Configuración de la aplicación
WIDTH, HEIGHT = 480, 320
FPS = 60

# Rutas de assets
ASSETS_PATHS = {
    'gif': "assets/media/intro_braillo.gif",
    'font': "assets/fonts/Coiny-Regular.ttf",
    'braille_font': "assets/fonts/ONCE_CBE_6G.ttf",
    'music': "assets/sounds/Background.ogg",
    'buttons': {
        'diccionario': "assets/images/icono_diccionario.png",
        'jugar': "assets/images/icono_jugar.png",
        'configurar': "assets/images/icono_configurar.png",
        'salir': "assets/images/icono_salir.png",
        'back': "assets/images/icono_regresar.png",
        'next': "assets/images/icono_siguiente.png",
        'menu': "assets/images/icono_menu.png",
        'musica_on': "assets/images/icono_volum.png",
        'musica_off': "assets/images/icono_vol_mute.png"
    },
    'images': {
        'world_map': "assets/images/mapa.png",
        'celdas_on': "assets/images/basico_1_on.png",
        'alfabeto_on': "assets/images/basico_2_on.png",
        'mayusculas_on': "assets/images/basico_3_on.png",
        'numeros_on': "assets/images/basico_4_on.png",
        'signos_on': "assets/images/basico_5_on.png",
        'desfinal_on': "assets/images/basico_6_on.png",
    }
}

# Función de cargar fuentes
def load_fonts():
    return {
        'tiny': pygame.font.Font(ASSETS_PATHS['font'], 16),
        'small': pygame.font.Font(ASSETS_PATHS['font'], 22),
        'default': pygame.font.Font(ASSETS_PATHS['font'], 32),
        'large': pygame.font.Font(ASSETS_PATHS['font'], 40),
        'big': pygame.font.Font(ASSETS_PATHS['font'], 48),
        'huge': pygame.font.Font(ASSETS_PATHS['font'], 64)
    }
