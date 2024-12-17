import unittest
import pandas as pd
from datetime import datetime
import os
from io import StringIO

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
        return [0.85]  # Simulación de predicción alta

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


# Pruebas de integración
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


# Generar reporte de pruebas
def generate_test_report():
    results = []
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    excel_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    # Ejecutar las pruebas
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(stream=StringIO(), verbosity=2)
    result = runner.run(suite)

    # Construir resultados en detalle
    for test in result.failures:
        results.append({"Test": str(test[0]), "Status": "Failed", "Details": test[1]})
    for test in result.errors:
        results.append({"Test": str(test[0]), "Status": "Error", "Details": test[1]})
    for test in suite:
        if str(test) not in [r["Test"] for r in results]:
            results.append({"Test": str(test), "Status": "Passed", "Details": "N/A"})

    # Guardar en archivo de texto
    with open(report_file, "w") as f:
        f.write("Reporte de Pruebas\n")
        f.write("==================\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de pruebas ejecutadas: {result.testsRun}\n")
        f.write(f"Fallos: {len(result.failures)}\n")
        f.write(f"Errores: {len(result.errors)}\n")
        f.write(f"Éxitos: {result.testsRun - len(result.failures) - len(result.errors)}\n\n")
        for item in results:
            f.write(f"Prueba: {item['Test']}\n")
            f.write(f"Estado: {item['Status']}\n")
            f.write(f"Detalles: {item['Details']}\n\n")

    # Guardar en Excel
    df = pd.DataFrame(results)
    df.to_excel(excel_file, index=False)

    print(f"Reporte generado en texto: {report_file}")
    print(f"Reporte generado en Excel: {excel_file}")


if __name__ == "__main__":
    generate_test_report()
