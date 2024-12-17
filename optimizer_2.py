import cProfile
import pstats
import numpy as np


class NeuralNetworkPredictor:
    def __init__(self):
        self.model_loaded = None  # Indicador de modelo cargado
        self.cache = {}  # Caché para resultados de predicción repetidos

    def load_model(self):
        """Carga el modelo solo si no está cargado."""
        if not self.model_loaded:
            # Simulación de carga de modelo costoso
            print("Cargando modelo de red neuronal...")
            self.model_loaded = "Modelo de red neuronal cargado"
        return self.model_loaded

    def predict(self, data):
        """Realiza una predicción basada en los datos de entrada."""
        if not self.model_loaded:
            raise ValueError("El modelo no está cargado.")
        
        # Generar un identificador único basado en los datos para la caché
        data_id = hash(data.tobytes())
        if data_id in self.cache:
            return self.cache[data_id]  # Retorna predicción de la caché
        
        # Simulación de predicción costosa
        prediction = np.dot(data, np.random.random(data.shape[1]))
        self.cache[data_id] = prediction  # Almacena en caché
        return prediction


# Simulación de entrada de datos y optimización
def simulate_predictions(predictor, data_list):
    for data in data_list:
        result = predictor.predict(data)
        print(f"Predicción: {result}")


# Perfilador para medir el rendimiento
def profile_predictions():
    predictor = NeuralNetworkPredictor()

    # Datos de entrada simulados
    data_list = [
        np.random.rand(1, 10),
        np.random.rand(1, 10),
        np.random.rand(1, 10),
        np.random.rand(1, 10),
    ]

    # Cargar el modelo
    predictor.load_model()

    profiler = cProfile.Profile()
    profiler.enable()

    # Ejecutar simulación de predicciones
    simulate_predictions(predictor, data_list)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("time")
    stats.print_stats(10)  # Mostrar las 10 funciones más lentas

    print("\nCaché de predicciones:")
    print(predictor.cache)  # Mostrar contenido de la caché


if __name__ == "__main__":
    print("Perfilando predicciones de la red neuronal...")
    profile_predictions()
