from locust import HttpUser, task, between, constant_pacing
import random
from datetime import datetime, timedelta

class UserBehavior(HttpUser):
    # Ajustar tiempos entre solicitudes para simular patrones realistas
    wait_time = constant_pacing(2)  # Mantiene un ritmo constante de 1 solicitud cada 2 segundos

    @task(3)  # Aumentar la prioridad del endpoint principal (3x más frecuente)
    def test_main_endpoint(self):
        self.client.get("/login")  # URL principal del sistema

    @task(1)  # Reducir la prioridad del endpoint de reporte (menos frecuente)
    def test_specific_endpoint(self):
        # Generar dinámicamente fechas aleatorias para simular datos de prueba variados
        fecha_inicio = (datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
        fecha_fin = datetime.now().strftime('%Y-%m-%d')

        self.client.post(
            "/reporte_indicador_fallos",
            json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
        )
