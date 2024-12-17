from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, send_file, current_app
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta
from xhtml2pdf import pisa
import io
import mysql.connector
from datetime import datetime
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import numpy as np


app = Flask(__name__)
app.secret_key = 'f38b01f41ceadcf299e2eba696140e03cbafc72ef88ed20d'
modelo = load_model('modelo_prediccion_fallos_optimizado.keras')


if not os.path.exists('logs'):
    os.mkdir('logs')

log_file = 'logs/monitoreo.log'

# RotatingFileHandler para limitar el tamaño del archivo de logs
handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)  # 1MB máximo por archivo, hasta 5 backups
handler.setLevel(logging.INFO)  # Nivel de logging por defecto (INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s - %(module)s:%(funcName)s (linea: %(lineno)d)')
handler.setFormatter(formatter)

# Añadir el handler al logger de Flask
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Andre2708@localhost/monitoreo_hardware'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'f38b01f41ceadcf299e2eba696140e03cbafc72ef88ed20d'
#app.secret_key = os.urandom(24)

db = SQLAlchemy(app)

# Servidor de Correo SMTPLIB
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
SMTP_USER = 'sistema.monitoreo.2024@gmail.com'
SMTP_PASSWORD = 'wizk bswx jdna njvu'

# Generador de token seguro
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Modelo para la tabla de usuarios
class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('administrador', 'tecnico'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    activo = db.Column(db.Boolean, nullable=False)

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Buscar la existencia del username en la tabla de la BD
        user = Usuarios.query.filter_by(username=username).first()

        # Comprueba si el usuario existe y si la contraseña es correcta
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id_usuario
            session['username'] = user.username
            session['nombre_completo'] = user.nombre_completo  # Guarda el nombre del usuario en la sesión
            session['rol'] = user.rol  # Guarda el rol en la sesión
            app.logger.info(f'Inicio de sesión exitoso por el usuario {username} con rol de {user.rol}')

            # Redirige según el rol del usuario
            if user.rol == 'administrador':
                return redirect(url_for('admin_dashboard'))
            elif user.rol == 'tecnico':
                return redirect(url_for('tecnico_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            app.logger.warning(f'Intento de inicio de sesión fallido para el usuario {username}')
            return redirect(url_for('login'))  # Redirige a la página de login si hay error

    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    username = session.get('username')
    session.pop('user_id', None)
    session.clear()
    flash('Sesión cerrada', 'info')
    app.logger.info(f'El usuario {username} cerró sesión')
    return redirect(url_for('login'))

# Mostrar mensaje de bienvenida en la vista por cada rol
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session:
        return render_template('admin_dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/tecnico_dashboard')
def tecnico_dashboard():
    if 'username' in session:
        return render_template('tecnico_dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))

# Ruta para crear usuarios (solo para el administrador)
@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if 'user_id' not in session or session['rol'] != 'administrador':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        nombre_completo = request.form['nombre_completo']
        email = request.form['email']
        rol = request.form['rol']

        nuevo_usuario = Usuarios(nombre_completo=nombre_completo, username=username, password=password, email=email, rol=rol, activo=True)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario creado con éxito', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('crear_usuario.html')

@app.route('/usuarios/editar_usuario/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    # Lógica para editar el usuario con el ID proporcionado
    usuario = Usuarios.query.get(id_usuario)

    if request.method == 'POST':
        # Actualizar los datos del usuario con el formulario recibido
        usuario.username = request.form['username']
        usuario.nombre_completo = request.form['nombre_completo']
        usuario.email = request.form['email']
        usuario.rol = request.form['rol']
        
        db.session.commit()
        flash('Usuario actualizado con éxito', 'success')
        return redirect(url_for('listar_usuarios'))

    # Renderizar el formulario de edición con los datos del usuario
    return render_template('editar_usuario.html', usuario=usuario)


@app.route('/desactivar_usuario/<int:id_usuario>', methods=['GET'])
def desactivar_usuario(id_usuario):
    usuario = Usuarios.query.get_or_404(id_usuario)
    usuario.activo = False
    db.session.commit()
    flash(f'Usuario {usuario.username} desactivado con éxito.', 'success')
    return redirect(url_for('listar_usuarios'))

@app.route('/activar_usuario/<int:id_usuario>', methods=['GET'])
def activar_usuario(id_usuario):
    usuario = Usuarios.query.get_or_404(id_usuario)
    usuario.activo = True
    db.session.commit()
    flash(f'Usuario {usuario.username} activado con éxito.', 'success')
    return redirect(url_for('listar_usuarios'))

@app.route('/listar_usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuarios.query.all()  # Obtiene todos los usuarios
    return render_template('listar_usuarios.html', usuarios=usuarios)

@app.route('/reportes_pdf_admin', methods=['GET'])
def reportes_pdf_admin():
    return render_template('reportes_pdf_admin.html')

@app.route('/reportes_pdf_tecnico', methods=['GET'])
def reportes_pdf_tecnico():
    return render_template('reportes_pdf_tecnico.html')

@app.route('/reportes_indicador_admin', methods=['GET'])
def reportes_indicador_admin():
    return render_template('reportes_indicador_admin.html')

@app.route('/deteccion_fallos', methods=['GET'])
def deteccion_fallos():
    return render_template('deteccion_fallos.html')

# Función para enviar correos usando smtplib
def send_email(to, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Conexión al servidor SMTP usando SSL
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to, msg.as_string())
        server.quit()
        print(f"Correo enviado a {to}")
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")

# Ruta para solicitar el restablecimiento de contraseña
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = get_user_by_email(email)

        if user:
            # Generar token de restablecimiento con tiempo de caducidad (1 hora)
            token = s.dumps(user['email'], salt='recover-password')
            expiration_time = datetime.now() + timedelta(hours=1)

            # Guardar el token y la fecha de expiración en la base de datos
            save_reset_token(user['id_usuario'], token, expiration_time)

            # Enviar correo de restablecimiento
            reset_url = url_for('reset_password', token=token, _external=True)
            subject = "Restablecer tu contraseña :: Sistema de Monitoreo"
            body = f'Haz clic en el siguiente enlace para restablecer tu contraseña: {reset_url}'
            send_email(user['email'], subject, body)
            flash('Se ha enviado un enlace de restablecimiento de contraseña a tu correo.', 'info')
            app.logger.info(f'Se solicitó restablecimiento de contraseña para el usuario {user['username']} con correo {email}')
            return redirect(url_for('login'))

        flash('No se encontró una cuenta con ese correo.', 'danger')
    
    return render_template('forgot_password.html')

# Ruta para restablecer la contraseña
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Validar el token (expira en 1 hora = 3600 segundos)
        email = s.loads(token, salt='recover-password', max_age=3600)
        user = get_user_by_email(email)

        if not user or user['reset_token'] != token:
            flash('Token inválido o expirado.', 'danger')
            app.logger.info(f'Token inválido o expirado para el usuario {user['username']}')
            return redirect(url_for('forgot_password'))

        if request.method == 'POST':
            new_password = request.form['password']
            hashed_password = generate_password_hash(new_password)

            # Actualizar la contraseña en la base de datos
            update_user_password(user['id_usuario'], hashed_password)

            flash('Tu contraseña ha sido actualizada exitosamente.', 'success')
            app.logger.info(f'Se realizo el cambio de contraseña para el usuario {user['username']}')
            return redirect(url_for('login'))

    except Exception as e:
        print(f"Error: {str(e)}")
        flash('El enlace de restablecimiento ha expirado o es inválido.', 'danger')
        app.logger.info(f'Expiró el restablecemiento de contraseña para el usuario {user['username']}')
        return redirect(url_for('forgot_password'))

    return render_template('reset_password.html', token=token)

# Funciones auxiliares para interactuar con la base de datos

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  
        user="root",      
        password="Andre2708", 
        database="monitoreo_hardware" 
    ) 


def get_user_by_email(email):
    conn = get_db_connection()  # Conexión a la base de datos MySQL
    cursor = conn.cursor(dictionary=True)  # Esto devuelve los resultados como diccionario

    # Consulta para obtener el usuario por correo
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    
    # Obtener el resultado de la consulta
    user = cursor.fetchone()

    # Cerrar la conexión a la base de datos
    conn.close()

    # Si se encuentra el usuario, devolverlo
    return user if user else None

def save_reset_token(user_id, token, expiration_time):
    conn = get_db_connection()  # Conexión a la base de datos MySQL
    cursor = conn.cursor()

    # Actualizar el token y la fecha de expiración en la tabla 'usuarios'
    cursor.execute("""
        UPDATE usuarios 
        SET reset_token = %s, reset_token_expiration = %s 
        WHERE id_usuario = %s
    """, (token, expiration_time, user_id))

    # Confirmar los cambios en la base de datos y cerrar la conexión
    conn.commit()
    conn.close()

def update_user_password(user_id, hashed_password):
    conn = get_db_connection()  # Conexión a la base de datos MySQL
    cursor = conn.cursor()

    # Actualizar la contraseña del usuario y eliminar el token y su fecha de expiración
    cursor.execute("""
        UPDATE usuarios 
        SET password = %s, reset_token = NULL, reset_token_expiration = NULL 
        WHERE id_usuario = %s
    """, (hashed_password, user_id))

    # Confirmar los cambios en la base de datos y cerrar la conexión
    conn.commit()
    conn.close()

@app.route('/reporte_inventario_hardware', methods=['GET'])
def reporte_inventario_hardware():
    tipo_equipo = request.args.get('tipo_equipo')
    estado_actual = request.args.get('estado_actual')

    # Conexión a la base de datos MySQL usando mysql-connector-python
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Para que los resultados sean en formato diccionario

    # Consulta JOIN entre las tablas equipos y hardware_monitoreado
    query = """
        SELECT 
            equipos.hostname, 
            equipos.tipo_equipo, 
            hardware_monitoreado.descripcion, 
            hardware_monitoreado.capacidad, 
            hardware_monitoreado.estado_actual
        FROM equipos
        JOIN hardware_monitoreado ON equipos.hostname = hardware_monitoreado.hostname
        WHERE 1=1
    """

    # Lista para almacenar los parámetros
    params = []

    # Agregar los filtros condicionalmente
    if tipo_equipo:
        query += " AND equipos.tipo_equipo = %s"
        params.append(tipo_equipo)

    if estado_actual:
        query += " AND hardware_monitoreado.estado_actual = %s"
        params.append(estado_actual)

    # Ejecutar la consulta con los parámetros
    cursor.execute(query, params)

    # Obtener los resultados
    hardware_data = cursor.fetchall()

    # Cerrar la conexión
    cursor.close()
    conn.close()

    # Renderizar el template con los datos
    return render_template('inventario_hardware.html', hardware_data=hardware_data)

@app.route('/reporte_alertas_hardware', methods=['GET'])
def reporte_alertas_hardware():
    # Conexión a la base de datos MySQL
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Resultados como diccionarios

    # Consulta para obtener las alertas de hardware
    query = """
        SELECT 
            a.id_alerta, 
            a.hostname, 
            a.descripcion, 
            a.tipo_hardware, 
            a.fecha_alerta, 
            a.generada_por_nn
        FROM alertas a
        JOIN equipos e ON a.hostname = e.hostname
    """

    cursor.execute(query)
    alertas_data = cursor.fetchall()

    # Cerrar la conexión
    cursor.close()
    conn.close()

    # Renderizar el template con los datos obtenidos
    return render_template('alertas_hardware.html', alertas_data=alertas_data)

@app.route('/reporte_estado_equipos', methods=['GET'])
def reporte_estado_equipos():
    # Conexión a la base de datos MySQL
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Resultados como diccionarios

    # Consulta para obtener el estado de los equipos
    query = """
        SELECT 
            e.hostname, 
            e.tipo_equipo, 
            h.descripcion, 
            h.capacidad, 
            h.estado_actual
        FROM equipos e
        JOIN hardware_monitoreado h ON e.hostname = h.hostname
    """

    cursor.execute(query)
    equipos_data = cursor.fetchall()

    # Cerrar la conexión
    cursor.close()
    conn.close()

    # Renderizar el template con los datos obtenidos
    return render_template('estado_equipos.html', equipos_data=equipos_data)

@app.route('/reporte_indicador_fallos', methods=['GET', 'POST'])
def reporte_indicador_fallos():
    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Variables para almacenar las fechas seleccionadas
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    # Convertir las fechas al formato correcto para MySQL si están presentes
    if fecha_inicio and fecha_fin:
        try:
            # Asegurarse de que las fechas estén en el formato correcto
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            return "Error: Formato de fecha incorrecto", 400

    print(f"Fecha inicio: {fecha_inicio}, Fecha fin: {fecha_fin}")  # Verificación en la consola

    # Consulta SQL para filtrar por rango de fechas
    query = """
    SELECT 
        a.hostname AS Hostname,
        SUM(TIMESTAMPDIFF(MINUTE, a.fecha_alerta, l.fecha_log)) AS "Suma de Tiempos de Detección",
        COUNT(a.id_alerta) AS "Número de Fallos (n)",
        ROUND(AVG(TIMESTAMPDIFF(MINUTE, a.fecha_alerta, l.fecha_log)), 0) AS "Tiempo Promedio de Detección"
    FROM 
        alertas a
    JOIN 
        logs_cambios l ON a.hostname = l.hostname 
                       AND TIMESTAMPDIFF(MINUTE, a.fecha_alerta, l.fecha_log) BETWEEN 0 AND 1200
    WHERE 
        l.fecha_log BETWEEN %s AND %s
    GROUP BY 
        a.hostname
    ORDER BY 
        Hostname;
    """

    # Ejecutar la consulta con las fechas como parámetros
    cursor.execute(query, (fecha_inicio, fecha_fin))

    # Obtener resultados
    results = cursor.fetchall()
    print(f"Resultados de la consulta: {results}")

    # Estructura de datos para pasar a la plantilla
    fallos_data = [
        {
            "hostname": row["Hostname"], 
            "suma_tiempos": row["Suma de Tiempos de Detección"], 
            "numero_fallos": row["Número de Fallos (n)"], 
            "tiempo_promedio": row["Tiempo Promedio de Detección"]
        }
        for row in results
    ]

    cursor.close()
    conn.close()

    return render_template('deteccion_fallos.html', fallos_data=fallos_data, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, enumerate=enumerate)


@app.route('/reporte_tasa_fallos', methods=['GET', 'POST'])
def reporte_tasa_fallos():
    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Variables para almacenar las fechas seleccionadas
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    # Convertir las fechas al formato correcto para MySQL si están presentes
    if fecha_inicio and fecha_fin:
        try:
            # Asegurarse de que las fechas estén en el formato correcto
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            return "Error: Formato de fecha incorrecto", 400

    print(f"Fecha inicio: {fecha_inicio}, Fecha fin: {fecha_fin}")  # Verificación en la consola

    # Consulta SQL para filtrar por rango de fechas
    query = """
    SELECT 
        hostname AS Hostname,
        SUM(tiempo_uso) AS "Tiempo Total de Uso",
        COUNT(id_tasa_fallo) AS "Número de Fallos (n)",
        ROUND(SUM(tiempo_uso) / COUNT(id_tasa_fallo), 2) AS "Tasa de Fallos por Activo"
    FROM 
        tasa_fallos_por_activo
    WHERE 
        fecha_fallo BETWEEN %s AND %s
    GROUP BY 
        hostname
    ORDER BY 
        Hostname;
    """

    # Ejecutar la consulta con las fechas como parámetros
    cursor.execute(query, (fecha_inicio, fecha_fin))

    # Obtener resultados
    results = cursor.fetchall()
    print(f"Resultados de la consulta: {results}")

    # Estructura de datos para pasar a la plantilla
    tasa_fallos_data = [
        {
            "hostname": row["Hostname"], 
            "tiempo_total_uso": row["Tiempo Total de Uso"], 
            "numero_fallos": row["Número de Fallos (n)"], 
            "tasa_fallos": row["Tasa de Fallos por Activo"]
        }
        for row in results
    ]

    cursor.close()
    conn.close()

    return render_template('tasa_fallos.html', tasa_fallos_data=tasa_fallos_data, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, enumerate=enumerate)

# Función para generar el PDF
def crear_pdf(template, datos):
    html = render_template(template, datos=datos)
    resultado_pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html.encode('UTF-8'), dest=resultado_pdf)
    if pisa_status.err:
        return None
    return resultado_pdf.getvalue()

def enviar_correo_alerta(alerta):
    # Lógica para enviar el correo
    destinatario = "fguanilo@contraloria.gob.pe"
    
    try:
        # Enviar correo...
        estado_envio = True  # envío exitoso
    except:
        estado_envio = False  # Si el envío falla
    
    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insertar el registro en la tabla envio_correos_alertas
    cursor.execute("""
        INSERT INTO envio_correos_alertas (id_alerta, fecha_envio, destinatario, estado_envio)
        VALUES (%s, NOW(), %s, %s)
    """, (alerta['id_alerta'], destinatario, estado_envio))
    
    conn.commit()
    cursor.close()
    conn.close()

# Ruta para exportar a PDF
@app.route('/generar_pdf')
def generar_pdf():
    datos = {'nombre': 'Ejemplo', 'descripcion': 'Prueba de PDF'}
    pdf = crear_pdf('template.html', datos)
    if pdf:
        return send_file(
            io.BytesIO(pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='reporte.pdf'
        )
    return 'Error al generar PDF'

# Modelo de la tabla equipos
class Equipos(db.Model):
    __tablename__ = 'equipos'
    hostname = db.Column(db.String(255), primary_key=True)
    sistema_operativo = db.Column(db.String(100))
    usuario_logueado = db.Column(db.String(255))
    tipo_equipo = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    serie = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())

# Modelo de la tabla hardware_monitoreado
class HardwareMonitoreado(db.Model):
    __tablename__ = 'hardware_monitoreado'
    id_hardware = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hostname = db.Column(db.String(255), db.ForeignKey('equipos.hostname'), nullable=False)
    tipo_hardware = db.Column(db.String(50))
    descripcion = db.Column(db.String(255))
    capacidad = db.Column(db.String(100))
    estado_actual = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    equipo = db.relationship('Equipos', backref=db.backref('hardware', lazy=True))

# Modelo de alertas
class Alerta(db.Model):
    __tablename__ = 'alertas'
    id_alerta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hostname = db.Column(db.String(255), db.ForeignKey('equipos.hostname'), nullable=False)
    descripcion = db.Column(db.String(255))
    tipo_hardware = db.Column(db.String(50))
    fecha_alerta = db.Column(db.DateTime, default=db.func.current_timestamp())

    equipo = db.relationship('Equipos', backref=db.backref('alertas', lazy=True))


scaler = StandardScaler()
datos_referencia = np.array([
    [75, 60, 50, 1, 65, 100],
    [85, 70, 60, 1, 75, 200],
    [50, 40, 30, 1, 50, 50],
    [95, 80, 70, 0, 85, 500]
])
scaler.fit(datos_referencia)

# Función para enviar alertas por correo electrónico
def enviar_correo_alerta(hostname, tipo_hardware, descripcion, tipo_alerta="cambio"):
    sender_email = "sistema.monitoreo.2024@gmail.com"
    receiver_email = "fguanilo@contraloria.gob.pe"
    password = "wizk bswx jdna njvu"
    
    # Personalizando el asunto y el cuerpo del mensaje
    if tipo_alerta == "cambio":
        subject = f"Alerta: Cambio detectado en {tipo_hardware} en {hostname}"
        body = f"""
        ¡Se ha detectado un cambio en el hardware del equipo {hostname}!

        Detalles del cambio:
        - Tipo de Hardware: {tipo_hardware}
        - Descripción: {descripcion}
        - Fecha y Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Revisa el estado del equipo lo antes posible.

        Atentamente,

        Sistema de Monitoreo de Hardware
        """
    elif tipo_alerta == "fallo":
        subject = f"Alerta: Fallo detectado en {tipo_hardware} en {hostname}"
        body = f"""
        ¡Se ha detectado un Fallo en el hardware del equipo {hostname}!

        Detalles del Fallo:
        - Tipo de Hardware: {tipo_hardware}
        - Descripción: {descripcion}
        - Fecha y Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Se recomienda verificar el equipo y resolver el fallo lo antes posible.

        Atentamente,

        Sistema de Monitoreo de Hardware
        """

    # Configuración del mensaje de correo
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Envío de correo
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"Correo de alerta enviado a {receiver_email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Predicción de fallos en hardware
@app.route('/predecir_fallo', methods=['POST'])
def predecir_fallo():
    datos = request.json['datos_hardware']
    hostname = request.json.get('hostame', '97621-cgr')
    tipo_hardware = 'Disco Duro'
    descripcion = "Posible fallo detectado según predicción de red neuronal"

    datos_normalizados = scaler.transform([datos])
    prediccion = modelo.predict(datos_normalizados)

    if prediccion[0][0] > 0.5:      #Umbral de probabilidad para alerta
        enviar_correo_alerta(
            hostname=hostname,
            tipo_hardware=tipo_hardware,
            descripcion=descripcion,
            tipo_alerta="fallo"
        )
        return jsonify({"alerta": "Posible fallo detectado"}), 200
    else:
        return jsonify({"alerta": "No hay fallos predichos"}), 200

# Ruta para recibir los datos del agente
@app.route('/update_hardware', methods=['POST'])
def update_hardware():
    data = request.json
    if not data or 'hostname' not in data:
        logging.error("Datos malformados recibidos")
        return jsonify({'status': 'error', 'message': 'Datos malformados'}), 400

    hostname = data.get('hostname')
    sistema_operativo = data.get('sistema_operativo', 'Desconocido')
    usuario_logueado = data.get('usuario_actual', 'Desconocido')
    tipo_equipo = data.get('tipo_equipo', 'Desconocido')
    marca = data.get('marca', 'Desconocido')
    modelo = data.get('modelo', 'Desconocido')
    serie = data.get('serie', 'Desconocido')

    # Comprobar si el equipo ya existe
    equipo = Equipos.query.filter_by(hostname=hostname).first()

    if not equipo:
        equipo = Equipos(
            hostname=hostname, 
            sistema_operativo=sistema_operativo,
            usuario_logueado=usuario_logueado,
            tipo_equipo=tipo_equipo,
            marca=marca,
            modelo=modelo,
            serie=serie,
            )
        db.session.add(equipo)
    else:
        # Actualizar detalles del equipo si es necesario
        equipo.sistema_operativo=sistema_operativo
        equipo.usuario_logueado=usuario_logueado
        equipo.tipo_equipo = tipo_equipo
        equipo.marca = marca
        equipo.modelo = modelo
        equipo.serie = serie
        db.session.commit()
        logging.info(f"Datos del equipo {hostname} actualizados correctamente")

        return jsonify({'status': 'success', 'message': 'Datos actualizados correctamente'}), 200

    cambios_detectados = []

    # Procesar CPU
    cpu_data = data.get('cpu', {})
    cpu_registrado = HardwareMonitoreado.query.filter_by(hostname=hostname, tipo_hardware='CPU').first()
    if cpu_registrado and (cpu_registrado.descripcion != cpu_data.get('nombre') or 
                           cpu_registrado.capacidad != f"{cpu_data.get('num_nucleos', 0)} Núcleos"):
        cambios_detectados.append(f"Cambio en CPU detectado en {hostname}")
        nueva_alerta = Alerta(hostname=hostname, descripcion='Cambio en CPU detectado', tipo_hardware='CPU')
        db.session.add(nueva_alerta)
        enviar_correo_alerta('Alerta de cambio de hardware', f"Se detectó un cambio en el Procesador del equipo {hostname}.")
    nuevo_hardware = HardwareMonitoreado(
        hostname=hostname,
        tipo_hardware='CPU',
        descripcion=cpu_data.get('nombre', 'Desconocido'),
        capacidad=f"{cpu_data.get('num_nucleos', 0)} Núcleos, {cpu_data.get('num_hilos', 0)} Hilos",
        estado_actual="Funcionando"
    )
    db.session.add(nuevo_hardware)

    # Procesar RAM
    ram_data = data.get('ram', {})
    ram_registrado = HardwareMonitoreado.query.filter_by(hostname=hostname, tipo_hardware='RAM').first()
    if ram_registrado and ram_registrado.descripcion != f"Total: {ram_data.get('total', 0)} GB":
        cambios_detectados.append(f"Cambio en RAM detectado en {hostname}")
        nueva_alerta = Alerta(hostname=hostname, descripcion='Cambio en RAM detectado', tipo_hardware='RAM')
        db.session.add(nueva_alerta)
        enviar_correo_alerta('Alerta de cambio de hardware', f"Se detectó un cambio en la Memoria RAM del equipo {hostname}.")
    nuevo_hardware = HardwareMonitoreado(
        hostname=hostname,
        tipo_hardware='RAM',
        descripcion=f"Total: {ram_data.get('total', 0)} GB",
        capacidad=f"Disponible: {ram_data.get('disponible', 0)} GB",
        estado_actual="Funcionando"
    )
    db.session.add(nuevo_hardware)

    # Procesar discos duros
    for disco in data.get('discos', []):
        disco_registrado = HardwareMonitoreado.query.filter_by(hostname=hostname, tipo_hardware='Disco Duro', descripcion=disco['dispositivo']).first()
        if disco_registrado and disco_registrado.capacidad != f"{disco['total']} GB":
            cambios_detectados.append(f"Cambio en Disco Duro detectado en {hostname}")
            nueva_alerta = Alerta(hostname=hostname, descripcion=f"Cambio en {disco['dispositivo']}", tipo_hardware='Disco Duro')
            db.session.add(nueva_alerta)
            enviar_correo_alerta(hostname, 'Disco Duro', f"Cambio detectado en el disco {disco['dispositivo']}. Tamaño actual: {disco['total']} GB")
        nuevo_hardware = HardwareMonitoreado(
            hostname=hostname,
            tipo_hardware='Disco Duro',
            descripcion=disco['dispositivo'],
            capacidad=f"{disco['total']} GB",
            estado_actual=f"Usado: {disco['usado']} GB, Libre: {disco['libre']} GB"
        )
        db.session.add(nuevo_hardware)

    # Procesar tarjeta de red inalámbrica
    wifi_data = data.get('tarjeta_wifi', {})
    wifi_registrado = HardwareMonitoreado.query.filter_by(hostname=hostname, tipo_hardware='Tarjeta de Red').first()
    if wifi_registrado and wifi_registrado.capacidad != ", ".join(wifi_data.get('direcciones', [])):
        cambios_detectados.append(f"Cambio en tarjeta de red detectado en {hostname}")
        nueva_alerta = Alerta(hostname=hostname, descripcion='Cambio en tarjeta de red detectado', tipo_hardware='Tarjeta de Red')
        db.session.add(nueva_alerta)
        enviar_correo_alerta('Alerta de cambio de hardware', f"Se detectó un cambio en la tarjeta de red del equipo {hostname}.")
    nuevo_hardware = HardwareMonitoreado(
        hostname=hostname,
        tipo_hardware='Tarjeta de Red',
        descripcion=wifi_data.get('nombre', 'Desconocido'),
        capacidad=", ".join(wifi_data.get('direcciones', [])),
        estado_actual="Conectada"
    )
    db.session.add(nuevo_hardware)

    # Fallo en el Procesador
    cpu_data = data.get('cpu', {})
    if cpu_data.get('nombre') == "Unknown" or cpu_data.get('num_nucleos', 0) == 0:
        enviar_correo_alerta(hostname, 'CPU', 'Fallo detectado en el procesador', tipo_alerta="fallo")

    # Fallo en la Memoria RAM
    ram_data = data.get('ram', {})
    if ram_data.get('total', 0) < 1:  # Ejemplo: total de RAM inesperadamente bajo
        enviar_correo_alerta(hostname, 'RAM', 'Fallo detectado en la memoria RAM', tipo_alerta="fallo")

    # Fallo en el Disco Duro
    for disco in data.get('discos', []):
        if disco['usado'] == disco['total']:  # Ejemplo: disco lleno o fallo en el reporte de espacio
            enviar_correo_alerta(hostname, 'Disco Duro', f'Fallo detectado en el disco {disco["dispositivo"]}', tipo_alerta="fallo")

    # Fallo en la Tarjeta de Red
    wifi_data = data.get('tarjeta_wifi', {})
    if not wifi_data.get('direcciones'):  # Ejemplo: sin conexión de red
        enviar_correo_alerta(hostname, 'Tarjeta de Red', 'Fallo detectado en la tarjeta de red', tipo_alerta="fallo")

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Datos actualizados correctamente'}), 200

# Ruta para visualizar los equipos y sus datos de hardware
@app.route('/ver_datos')
def ver_datos():
    try:
        # Consulta para obtener los datos de equipos, hardware y alertas
        equipos = db.session.query(Equipos).all()
        hardware = db.session.query(HardwareMonitoreado).all()
        #alertas = db.session.query(alertas).all()

        # Asegúrate de que las variables se pasen a la plantilla
        return render_template('ver_datos.html', equipos=equipos, hardware=hardware)

    except Exception as e:
        return f"Ha ocurrido un error: {str(e)}"

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Error 500: {error}')
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f'Error 404: {request.url}')
    return render_template('404.html'), 404

# Iniciar el servidor Flask
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)