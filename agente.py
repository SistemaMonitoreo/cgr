import psutil
import platform
import requests
import json
import socket
import wmi
import os
import getpass

# Dirección del servidor web
SERVER_URL = 'http://localhost:5000/update_hardware'

# Función para obtener información del sistema
def obtener_informacion_equipo():
    # Obtener información del sistema operativo
    sistema_operativo = f"{platform.system()} {platform.release()}"

    # Obtener usuario logueado
    usuario_actual = getpass.getuser()

    # WMI para obtener marca, modelo y número de serie
    c = wmi.WMI()

    for os in c.Win32_OperatingSystem():
        version = os.Version  # Obtiene la versión completa de Windows
        build_number = os.BuildNumber  # Obtiene el número de compilación
        sistema_operativo += f" (Versión: {version}, Compilación: {build_number})"

    # Marca y modelo
    for system in c.Win32_ComputerSystem():
        marca = system.Manufacturer
        modelo = system.Model

    # Número de serie
    for bios in c.Win32_BIOS():
        serie = bios.SerialNumber

    # Tipo de equipo (puede depender de la lógica de tu empresa)
    tipo_equipo = "Portátil" if "Laptop" in modelo else "Estación de trabajo"

    # Información del procesador
    cpu_info = {
        'nombre': platform.processor(),
        'num_nucleos': psutil.cpu_count(logical=False),
        'num_hilos': psutil.cpu_count(logical=True)
    }

    # Información de la memoria RAM
    ram_info = {
        'total': psutil.virtual_memory().total // (1024 ** 3),  # Total en GB
        'disponible': psutil.virtual_memory().available // (1024 ** 3)  # Disponible en GB
    }

    # Información del disco duro
    discos = []
    for particion in psutil.disk_partitions():
        uso_disco = psutil.disk_usage(particion.mountpoint)
        discos.append({
            'dispositivo': particion.device,
            'total': uso_disco.total // (1024 ** 3),  # GB
            'usado': uso_disco.used // (1024 ** 3),
            'libre': uso_disco.free // (1024 ** 3)
        })

    # Información de la tarjeta de red inalámbrica
    interfaces_red = psutil.net_if_addrs()
    wifi_info = {}
    for iface, addrs in interfaces_red.items():
        if 'Wi-Fi' in iface or 'wlan' in iface.lower():  # Filtrar por interfaz Wi-Fi
            wifi_info = {
                'nombre': iface,
                'direcciones': [addr.address for addr in addrs if addr.family == socket.AF_INET]  # Solo IPv4
            }

    # Construir la estructura de datos del equipo
    datos_equipo = {
        'hostname': platform.node(),
        'usuario_actual': usuario_actual,
        'sistema_operativo': sistema_operativo,
        'tipo_equipo': tipo_equipo,
        'marca': marca,
        'modelo': modelo,
        'serie': serie,
        'cpu': cpu_info,
        'ram': ram_info,
        'discos': discos,
        'tarjeta_wifi': wifi_info,
        #'garantia_vencimiento': garantia_vencimiento
    }

    # Imprimir los datos obtenidos para verificar
    print(json.dumps(datos_equipo, indent=4))

    return datos_equipo

# Función para enviar los datos al servidor
def enviar_datos_servidor(datos_equipo):
    try:
        response = requests.post(SERVER_URL, json=datos_equipo)
        if response.status_code == 200:
            print("Datos enviados correctamente.")
        else:
            print(f"Error al enviar los datos: {response.status_code}")
    except Exception as e:
        print(f"Error al conectar con el servidor: {e}")

if __name__ == '__main__':
    datos_equipo = obtener_informacion_equipo()
    enviar_datos_servidor(datos_equipo)