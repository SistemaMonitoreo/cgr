import unittest
import numpy as np
from datetime import datetime

# Simulación de funciones del sistema
class DataCollector:
    def collect_data(self):
        return {
            "processor": "Intel Core i7",
            "ram": "16GB",
            "disk": "512GB SSD",
            "wifi_card": "Intel AX200"
        }

class NeuralNetworkPredictor:
    def __init__(self, model_loaded=True):
        self.model_loaded = model_loaded

    def predict(self, data):
        if not self.model_loaded:
            raise ValueError("Model not loaded.")
        return np.array([0.85])  # Simulación de predicción alta

class IndicatorVisualizer:
    def generate_graph(self, data, graph_type):
        if not data:
            raise ValueError("No data provided.")
        if graph_type not in ["bar", "line", "pie"]:
            raise ValueError("Invalid graph type.")
        return f"{graph_type}_graph_generated"

    def export_to_format(self, data, file_format):
        if not data:
            raise ValueError("No data to export.")
        if file_format not in ["pdf", "excel", "csv"]:
            raise ValueError("Invalid file format.")
        return f"data_exported_to_{file_format}"

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


# Clase de pruebas 1: Flujo sin alertas
class TestNoAlertIntegration(unittest.TestCase):

    def setUp(self):
        self.collector = DataCollector()
        self.predictor = NeuralNetworkPredictor()
        self.alert_generator = AlertGenerator()

    def test_no_alert_generated(self):
        data = self.collector.collect_data()
        self.assertIn("processor", data)
        prediction = self.predictor.predict(data)
        self.assertAlmostEqual(prediction[0], 0.85, places=2)
        result = self.alert_generator.generate_alert(hardware_change=False, prediction=0.5, threshold=0.8)
        self.assertEqual(result, "No alert generated.")
        self.assertEqual(len(self.alert_generator.alerts), 0)


# Clase de pruebas 2: Flujo con error en la predicción
class TestPredictionErrorIntegration(unittest.TestCase):

    def setUp(self):
        self.collector = DataCollector()
        self.alert_generator = AlertGenerator()

    def test_prediction_error_handling(self):
        data = self.collector.collect_data()
        self.assertIn("processor", data)
        predictor = NeuralNetworkPredictor(model_loaded=False)
        with self.assertRaises(ValueError):
            predictor.predict(data)
        result = self.alert_generator.generate_alert(hardware_change=True, prediction=0.0)
        self.assertEqual(result, "Alert generated.")
        self.assertEqual(len(self.alert_generator.alerts), 1)


# Clase de pruebas 3: Validación de exportación de gráficos
class TestVisualizationIntegration(unittest.TestCase):

    def setUp(self):
        self.collector = DataCollector()
        self.visualizer = IndicatorVisualizer()

    def test_graph_export(self):
        data = self.collector.collect_data()
        graph_result = self.visualizer.generate_graph(data, "bar")
        self.assertEqual(graph_result, "bar_graph_generated")
        export_result = self.visualizer.export_to_format(data, "pdf")
        self.assertEqual(export_result, "data_exported_to_pdf")


# Ejecutar todas las pruebas
if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)
