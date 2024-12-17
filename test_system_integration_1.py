import unittest
import numpy as np
from datetime import datetime

# Módulos simulados
class DataCollector:
    def collect_data(self):
        return {
            "processor": "Intel Core i7",
            "ram": "16GB",
            "disk": "512GB SSD",
            "wifi_card": "Intel AX200"
        }

class NeuralNetworkPredictor:
    def predict(self, data):
        # Simula una predicción basada en datos de entrada
        return np.array([0.85])  # Probabilidad de fallo

class IndicatorVisualizer:
    def generate_graph(self, data, graph_type):
        if not data:
            raise ValueError("No data provided.")
        if graph_type not in ["bar", "line", "pie"]:
            raise ValueError("Invalid graph type.")
        return f"{graph_type}_graph_generated"

class AlertGenerator:
    def __init__(self):
        self.alerts = []

    def generate_alert(self, hardware_change, prediction, threshold=0.8):
        if not hardware_change and prediction < threshold:
            return "No alert generated."
        alert = {
            "timestamp": datetime.now(),
            "type": "hardware" if hardware_change else "prediction",
            "details": {
                "hardware_change": hardware_change,
                "prediction": prediction
            }
        }
        self.alerts.append(alert)
        return "Alert generated."

# Pruebas de integración
class TestSystemIntegration(unittest.TestCase):
    
    def setUp(self):
        self.collector = DataCollector()
        self.predictor = NeuralNetworkPredictor()
        self.visualizer = IndicatorVisualizer()
        self.alert_generator = AlertGenerator()

    def test_full_integration_flow(self):
        # Paso 1: Recolección de datos
        data = self.collector.collect_data()
        self.assertIn("processor", data)
        self.assertIn("ram", data)
        
        # Paso 2: Predicción basada en los datos
        prediction = self.predictor.predict(data)
        self.assertAlmostEqual(prediction[0], 0.85, places=2)
        
        # Paso 3: Visualización de indicadores
        graph_result = self.visualizer.generate_graph(data, "bar")
        self.assertEqual(graph_result, "bar_graph_generated")
        
        # Paso 4: Generación de alertas
        alert_result = self.alert_generator.generate_alert(hardware_change=True, prediction=prediction[0])
        self.assertEqual(alert_result, "Alert generated.")
        self.assertEqual(len(self.alert_generator.alerts), 1)  # Verificar que se generó una alerta

# Ejecutar pruebas de integración
if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)
