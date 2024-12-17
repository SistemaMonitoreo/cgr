import cProfile
import pstats
from datetime import datetime

class AlertGenerator:
    def __init__(self):
        self.alerts = []  # Registro de alertas generadas
        self.alert_cache = set()  # Caché para evitar alertas duplicadas

    def generate_alert(self, hardware_change, prediction, threshold=0.8):
        # Crear un identificador único basado en el evento
        alert_id = f"{hardware_change}-{prediction:.2f}-{threshold:.2f}"
        if alert_id in self.alert_cache:  # Validar si la alerta ya existe
            return "Duplicate alert ignored."

        # Generar alerta solo si cumple condiciones
        if not hardware_change and prediction < threshold:
            return "No alert generated."

        # Registrar la alerta
        alert = {
            "timestamp": '2024-11-09 09:30:15',
            "type": "hardware" if hardware_change else "prediction",
            "details": {
                "hardware_change": hardware_change,
                "prediction": prediction
            }
        }
        self.alerts.append(alert)
        self.alert_cache.add(alert_id)  # Agregar al caché
        return "Alert generated."

    def list_alerts(self):
        return self.alerts


# Función para simular generación de alertas
def simulate_alerts(generator, hardware_changes, predictions, threshold):
    for hc, pred in zip(hardware_changes, predictions):
        result = generator.generate_alert(hardware_change=hc, prediction=pred, threshold=threshold)
        print(f"Alert result: {result}")


# Perfilador para medir el rendimiento
def profile_alert_generation():
    generator = AlertGenerator()

    # Simulación de datos
    hardware_changes = [True, False, True, False, True, False, True, False]
    predictions = [0.9, 0.5, 0.85, 0.7, 0.9, 0.5, 0.85, 0.7]
    threshold = 0.8

    profiler = cProfile.Profile()
    profiler.enable()

    # Ejecutar simulación de generación de alertas
    simulate_alerts(generator, hardware_changes, predictions, threshold)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("time")
    stats.print_stats(10)  # Mostrar las 10 funciones más lentas

    # Mostrar el registro de alertas generadas
    print("\nGenerated Alerts:")
    for alert in generator.list_alerts():
        print(alert)


if __name__ == "__main__":
    print("Profiling Alert Generation...")
    profile_alert_generation()

