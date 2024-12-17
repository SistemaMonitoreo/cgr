import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# Conexión a la base de datos MySQL
engine = create_engine('mysql+mysqlconnector://root:Andre2708@localhost/monitoreo_hardware')

# Cargar los datos desde los archivos CSV (asegúrate de que la ruta es correcta)
fallos_nn_df = pd.read_csv('D:/Usuarios/Administrador/Desktop/Tabla_fallos_nn.csv')
print("Archivo Tabla_fallos_nn.csv cargado correctamente")

alertas_df = pd.read_csv('D:/Usuarios/Administrador/Desktop/Tabla_Alertas.csv')
print("Archivo Tabla_Alertas.csv cargado correctamente")

# Parámetros constantes de entrenamiento
tasa_aprendizaje = 0.001
epocas = 10

# Calcular precisión y tasa de error
def calcular_precision_y_error(fallos_df, alertas_df):
    total_fallos = len(fallos_df)
    predichos_correctamente = len(alertas_df[alertas_df['generada_por_nn'] == 1])
    
    if total_fallos > 0:
        precision = (predichos_correctamente / total_fallos) * 100
        tasa_error = 100 - precision
    else:
        precision = 0
        tasa_error = 100
    return precision, tasa_error

# Obtener precisión y tasa de error para cada tipo de hardware y hostname
precision, tasa_error = calcular_precision_y_error(fallos_nn_df, alertas_df)

# Función para registrar datos de entrenamiento en la base de datos
def registrar_entrenamiento_desde_historico(fallos_nn_df):
    query = text("""
    INSERT INTO entrenamiento_nn (hostname, tipo_hardware, epocas, tasa_aprendizaje, precision1, tasa_error, fecha_entrenamiento)
    VALUES (:hostname, :tipo_hardware, :epocas, :tasa_aprendizaje, :precision, :tasa_error, :fecha_entrenamiento)
    """)
    
    # Insertar cada registro de forma individual
    with engine.connect() as connection:
        for _, row in fallos_nn_df.iterrows():
            registro = {
                'hostname': row['hostname'],
                'tipo_hardware': row['tipo_hardware'],
                'epocas': epocas,
                'tasa_aprendizaje': tasa_aprendizaje,
                'precision': precision,
                'tasa_error': tasa_error,
                'fecha_entrenamiento': datetime.now()
            }
            print("Intentando insertar:", registro)  # Confirmar datos a insertar
            connection.execute(query, registro)  # Pasar como diccionario
            connection.commit()

# Llamar a la función para registrar los datos en la tabla entrenamiento_nn
registrar_entrenamiento_desde_historico(fallos_nn_df)
