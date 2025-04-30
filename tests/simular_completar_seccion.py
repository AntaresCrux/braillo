import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from core.progress_manager import ProgressManager
from utils.estructura_basico import estructura_basico

def simular_completar_seccion(nivel_id, seccion_id):
    """
    Aquí marcamos todos los ejercicios de una sección como completados en el progress.json
    """
    pm = ProgressManager()

    try:
        ejercicios = estructura_basico[nivel_id][seccion_id]["ejercicios"]
    except KeyError:
        print(f"Error: Nivel '{nivel_id}' o sección '{seccion_id}' no encontrados en estructura_basico.")
        return

    for ejercicio in ejercicios:
        pm.mark_exercise_done(nivel_id, seccion_id, ejercicio["nombre"])

    print(f"Sección '{seccion_id}' del nivel '{nivel_id}' simulada como completada.")

if __name__ == "__main__":
    # Aquí cambiamos los valores para simular otra sección
    nivel_id = "basico_1"
    seccion_id = "alfabeto" #Sección a simular
    
    simular_completar_seccion(nivel_id, seccion_id)
