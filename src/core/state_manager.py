#(Cambia entre pantallas como un FSM)
class StateManager:
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.current_name = None

    def add_state(self, name, state_instance):
        self.states[name] = state_instance

    def set_state(self, name):
        if name in self.states:
            self.current_state = self.states[name]
            self.current_name = name
        else:
            raise ValueError(f"Estado '{name}' no registrado.")

    def get_state(self):
        return self.current_name

    def handle_event(self, event):
        if self.current_state and hasattr(self.current_state, "handle_event"):
            return self.current_state.handle_event(event)

    def update(self, dt):
        if self.current_state and hasattr(self.current_state, "update"):
            result = self.current_state.update(dt)
            if isinstance(result, str) and result in self.states:
                self.set_state(result)

    def draw(self):
        if self.current_state and hasattr(self.current_state, "draw"):
            self.current_state.draw()
