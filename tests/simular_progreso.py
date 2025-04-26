import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from core.progress_manager import ProgressManager
from utils.estructura_basico import estructura_basico

def simular_completar_seccion(nivel_id, seccion):
    pm = ProgressManager()
    ejercicios = estructura_basico[nivel_id][seccion]["ejercicios"]

    for ejercicio in ejercicios:
        pm.mark_exercise_done(nivel_id, seccion, ejercicio["nombre"])

    print(f"Sección '{seccion}' del nivel '{nivel_id}' simulada como completada.")

if __name__ == "__main__":
    simular_completar_seccion("basico_1", "Celdas")
