import os
import binascii

# Generar una clave secreta de 24 bytes
secret_key = binascii.hexlify(os.urandom(24)).decode()
print(secret_key)