from werkzeug.security import generate_password_hash

# Genera la contraseña encriptada
password_plano = '20142'
password_encriptada = generate_password_hash(password_plano)

# Imprime la contraseña encriptada
print(f'Contraseña encriptada: {password_encriptada}')