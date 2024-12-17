import pandas as pd
import numpy as np

# Definir cantidad de datos simulados
n_rows = 1200

# Simulación de valores de hardware
cpu_usage = np.random.uniform(50, 100, n_rows)
ram_usage = np.random.uniform(40, 90, n_rows)
disk_usage = np.random.uniform(30, 80, n_rows)
network_status = np.random.choice([0, 1], n_rows)
temperature = np.random.uniform(40, 90, n_rows)
uptime = np.random.uniform(10, 500, n_rows)

# Definir fallos según condiciones simuladas
fallo = ((cpu_usage > 85) | (ram_usage > 75) | (disk_usage > 70) | (temperature > 80)).astype(int)

# Crear DataFrame y guardar
df = pd.DataFrame({
    'cpu_usage': cpu_usage,
    'ram_usage': ram_usage,
    'disk_usage': disk_usage,
    'network_status': network_status,
    'temperature': temperature,
    'uptime': uptime,
    'fallo': fallo
})

# Guardar como CSV
df.to_csv("D:/Usuarios/Administrador/Downloads/hardware_data_simulated.csv", index=False)
