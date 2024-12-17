import unittest
from app import app

class TestUpdateHardware(unittest.TestCase):
    def setUp(self):
        # Configuración inicial para cada prueba
        self.app = app.test_client()  # Cliente de pruebas para simular solicitudes
        self.app.testing = True       # Modo de pruebas activado

    def test_datos_validos(self):
        # Enviar datos válidos
        datos = {
            "hostname": "test-host",
            "sistema_operativo": "Windows 10",
            "usuario_actual": "admin"
        }
        response = self.app.post('/update_hardware', json=datos)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Datos actualizados correctamente', response.get_json()['message'])