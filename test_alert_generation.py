import unittest
from datetime import datetime

# Simulación de funciones del módulo de generación de alertas
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

    def send_alert(self, alert, method):
        if method not in ["email", "teams"]:
            raise ValueError("Invalid alert method.")
        return f"Alert sent via {method}"

    def log_alert(self, alert):
        if not alert:
            raise ValueError("No alert to log.")
        return f"Alert logged: {alert}"


# Creación de pruebas unitarias con unittest
class TestAlertGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = AlertGenerator()

    # Prueba 1: Validar generación de alertas
    def test_generate_alert(self):
        alert_1 = self.generator.generate_alert(hardware_change=True, prediction=0.9)
        alert_2 = self.generator.generate_alert(hardware_change=False, prediction=0.7)
        self.assertEqual(alert_1, "Alert generated.")
        self.assertEqual(alert_2, "No alert generated.")
        self.assertEqual(len(self.generator.alerts), 1)  # Solo se genera una alerta

    # Prueba 2: Validar envío de alertas
    def test_send_alert(self):
        alert = {"type": "hardware", "details": {"hardware_change": True, "prediction": 0.9}}
        self.assertEqual(self.generator.send_alert(alert, "email"), "Alert sent via email")
        self.assertEqual(self.generator.send_alert(alert, "teams"), "Alert sent via teams")
        with self.assertRaises(ValueError):
            self.generator.send_alert(alert, "sms")  # Método no válido

    # Prueba 3: Validar registro de alertas
    def test_log_alert(self):
        alert = {"type": "hardware", "details": {"hardware_change": True, "prediction": 0.9}}
        logged_message = self.generator.log_alert(alert)
        self.assertEqual(logged_message, f"Alert logged: {alert}")
        with self.assertRaises(ValueError):
            self.generator.log_alert(None)  # Intento de registrar una alerta nula


# Ejecutar pruebas unitarias
if __name__ == "__main__":
    unittest.main()
