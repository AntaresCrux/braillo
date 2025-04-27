import pygame
from ui.coverflow import CoverFlow
from ui.ui_helpers import update_and_draw_particles, create_particles
from utils.settings import WIDTH, HEIGHT
from ui.popup_message import PopupMessage  
from utils.states import AppStates
from utils.colors import BACKGROUND_COLOR

class Menu:
    def __init__(self, assets):
        self.state = AppStates.MENU
        self.assets = assets
        self.screen = pygame.display.get_surface()
        # Animación de partículas
        self.particles = create_particles(amount=30, screen_width=WIDTH, screen_height=HEIGHT)

        ordered_keys = ['diccionario', 'jugar', 'configurar', 'salir']
        buttons = [self.assets.buttons[key] for key in ordered_keys]
        self.coverflow = CoverFlow(buttons, font=assets.fonts['big'])
        self.button_actions = ['diccionario', 'jugar', 'configurar', 'salir']

        self.exit_popup = None  # ← NUEVO

        print("Botones cargados:", buttons)

    def update(self, dt):
        self.coverflow.update(dt)
        #update_and_draw_particles(self.particles, self.screen, dt=1/60)
        # Actualiza las partículas
        for particle in self.particles:
            particle.update(dt)

    def handle_event(self, event):
        # Dibuja las partículas
        #update_and_draw_particles(self.particles, self.screen, dt=1/60)

        if self.exit_popup and self.exit_popup.visible:
            self.exit_popup.handle_event(event)
            return None  # bloquea eventos mientras está abierto

        if self.state == AppStates.MENU:
            result = self.coverflow.handle_event(event)
            if result is not None:
                selected = self.button_actions[result]
                if selected == "jugar":
                    return "select_level"
                elif selected == "diccionario":
                    return "sin_escena"
                elif selected == "configurar":
                    return "configurar"
                elif selected == "salir":
                    self._mostrar_confirmacion_salida()
        return None

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        # Dibuja primero las partículas
        for particle in self.particles:
            particle.draw(self.screen)

        self.coverflow.draw(self.screen)
        if self.exit_popup and self.exit_popup.visible:
            self.exit_popup.draw()
        pygame.display.flip()

    def _mostrar_confirmacion_salida(self):
        self.exit_popup = PopupMessage(
            screen=self.screen,
            font_title=self.assets.fonts['big'],
            font_text=self.assets.fonts['default'],
            title="Confirmación",
            message="¿Estás seguro que deseas salir?",
            btn_texts=("Cancelar", "Sí"),
            on_close=lambda: self.exit_popup.hide(),
            on_next=self._salir_aplicacion,
            show_next=True
        )
        self.exit_popup.show()

    def _salir_aplicacion(self):
        pygame.quit()
        exit()
