

# Creacion de un nuevo usuario 01_newuser

import mysql.connector
from datetime import datetime
import os

# Definir la función log_error si no está importada
log_dir = r"C:\1wdoc\logs"

def log_error(message):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(log_dir, f"log_{current_time}.txt")
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

# Conexión a la base de datos MySQL
def crear_usuario(id_user, name_user, mail, imap_host, username, password):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Matkus2107",
            database="1w"
        )

        cursor = connection.cursor()

        # Comprobar si el usuario ya existe
        cursor.execute("SELECT COUNT(*) FROM users WHERE id_user = %s", (id_user,))
        resultado = cursor.fetchone()
        if resultado[0] > 0:
            log_error(f"El usuario {id_user} ya existe.")
            return False

        # Insertar el nuevo usuario
        cursor.execute("""
            INSERT INTO users (id_user, name_user, mail, imap_host, username, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_user, name_user, mail, imap_host, username, password))

        # Confirmar la inserción
        connection.commit()
        print(f"Usuario {id_user} creado correctamente.")
        return True

    except mysql.connector.Error as err:
        log_error(f"Error al conectar o insertar en MySQL: {err}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Ejemplo de uso: Crear un nuevo usuario
nuevo_usuario = "10003"
nombre_usuario = "Chevi"
correo = "jlu@ejemplo.com"
imap_host = "imap.gmail.com"
username = "jlu"
password = "contraseña_segura"

crear_usuario(nuevo_usuario, nombre_usuario, correo, imap_host, username, password)
