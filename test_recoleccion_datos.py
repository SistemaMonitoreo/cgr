import unittest
from app import app

# Simulación de funciones del módulo de recolección de datos
class DataCollector:
    def __init__(self, server_status):
        self.server_status = server_status  # Estado del servidor (conectado/desconectado)
    
    def connect_to_server(self):
        if self.server_status:
            return "Connected"
        else:
            return "Connection Failed"
    
    def collect_data(self):
        return {
            "processor": "Intel Core i7",
            "ram": "16GB",
            "disk": "512GB SSD",
            "wifi_card": "Intel AX200"
        }
    
    def collection_frequency(self, interval):
        return interval  # Simulación de frecuencia de recolección en segundos


# Creación de pruebas unitarias con unittest
class TestDataCollector(unittest.TestCase):

    # Prueba 1: Validar conexión del agente con el servidor
    def test_connect_to_server(self):
        collector_connected = DataCollector(True)
        collector_disconnected = DataCollector(False)
        self.assertEqual(collector_connected.connect_to_server(), "Connected")
        self.assertEqual(collector_disconnected.connect_to_server(), "Connection Failed")

    # Prueba 2: Validar la integridad de los datos recolectados
    def test_collect_data_integrity(self):
        collector = DataCollector(True)
        data = collector.collect_data()
        self.assertIn("processor", data)
        self.assertIn("ram", data)
        self.assertIn("disk", data)
        self.assertIn("wifi_card", data)
        self.assertNotEqual(data["processor"], "")
        self.assertNotEqual(data["ram"], "")
        self.assertNotEqual(data["disk"], "")
        self.assertNotEqual(data["wifi_card"], "")

    # Prueba 3: Validar frecuencia de recolección
    def test_collection_frequency(self):
        collector = DataCollector(True)
        self.assertEqual(collector.collection_frequency(5), 5)
        self.assertEqual(collector.collection_frequency(10), 10)
        self.assertEqual(collector.collection_frequency(0), 0)


# Ejecutar pruebas unitarias
if __name__ == "__main__":
    unittest.main()
