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
    'music': "assets/sounds/intro2.ogg",
    'buttons': {
        'diccionario': "assets/images/icono_diccionario.png",
        'jugar': "assets/images/icono_jugar.png",
        'configurar': "assets/images/icono_configurar.png",
        'salir': "assets/images/icono_salir.png",
        'back': "assets/images/icono_regresar.png",
        'next': "assets/images/icono_siguiente.png",
        'check': "assets/images/icono_correcto.png",
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
        'celda_base': "assets/images/celda.png",
    },
    "fichas": {
        "prefijo": "assets/images/numeros_braille/prefijo_numero.png",
        "numeros": {
            "0": "assets/images/numeros_braille/0.png",
            "1": "assets/images/numeros_braille/1.png",
            "2": "assets/images/numeros_braille/2.png",
            "3": "assets/images/numeros_braille/3.png",
            "4": "assets/images/numeros_braille/4.png",
            "5": "assets/images/numeros_braille/5.png",
            "6": "assets/images/numeros_braille/6.png",
            "7": "assets/images/numeros_braille/7.png",
            "8": "assets/images/numeros_braille/8.png",
            "9": "assets/images/numeros_braille/9.png"
        },
        "separadores": {
            "miles": "assets/images/numeros_braille/separador_miles.png",
            "decimal": "assets/images/numeros_braille/separador_decimal.png"
        },
        "signos": {
            "." and "...": "assets/images/signos_braille/punto.png",
            ",": "assets/images/signos_braille/coma.png",
            ";": "assets/images/signos_braille/punto-coma.png",
            ":": "assets/images/signos_braille/dos-puntos.png",
            "-": "assets/images/signos_braille/guion.png",
            "¿" and  "?": "assets/images/signos_braille/interrogacion.png",
            "¡" and "!": "assets/images/signos_braille/admiracion.png",
            "“" and "”": "assets/images/signos_braille/comillas-dobles.png",
            "(": "assets/images/signos_braille/parentesis-apertura.png",
            ")": "assets/images/signos_braille/parentesis-cierre.png",
        }
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
