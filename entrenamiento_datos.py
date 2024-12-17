import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Cargar datos de hardware (simulados)
data = pd.read_csv('D:/Usuarios/Administrador/Downloads/hardware_data.csv')
X = data.drop(columns=['fallo'])
y = data['fallo']

# Preprocesamiento de datos
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Creando el modelo de red neuronal
model = Sequential([
    Dense(64, input_shape=(X_train.shape[1],), activation='relu'),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])

# Compilando y entrenando el modelo optimizado
new_optimizer = Adam(learning_rate=0.0001)
model.compile(optimizer=new_optimizer, loss='binary_crossentropy', metrics=['accuracy'])
history = model.fit(X_train, y_train, epochs=100, validation_split=0.2, batch_size=16)

# Guardando el modelo entrenado
model.save('modelo_prediccion_fallos_optimizado.keras')