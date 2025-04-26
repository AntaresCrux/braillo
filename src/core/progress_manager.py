import json
from pathlib import Path

PROGRESS_PATH = Path("progress.json")

class ProgressManager:
    def __init__(self):
        self.data = self._load_progress()

    def _load_progress(self):
        if PROGRESS_PATH.exists():
            with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_progress(self):
        with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get_completed(self, nivel_id, seccion):
        return self.data.get(nivel_id, {}).get(seccion, [])

    def mark_exercise_done(self, nivel_id, seccion, ejercicio):
        if nivel_id not in self.data:
            self.data[nivel_id] = {}
        if seccion not in self.data[nivel_id]:
            self.data[nivel_id][seccion] = []
        if ejercicio not in self.data[nivel_id][seccion]:
            self.data[nivel_id][seccion].append(ejercicio)
            self.save_progress()

    def is_nivel_completo(self, seccion_id, estructura):
        nivel = estructura.get("basico_1", {})  # Siempre trabajamos con basico_1
        datos = nivel.get(seccion_id, {})
        ejercicios = datos.get("ejercicios", [])

        esperados = [e["nombre"] for e in ejercicios]
        hechos = self.get_completed("basico_1", seccion_id)

        return all(e in hechos for e in esperados)

