# config/database.py

import mysql.connector
from mysql.connector import Error
from modules.aa_logger import log_error

def connect_db():
    try:
        # Establecer la conexión con la base de datos MySQL
        connection = mysql.connector.connect(
            host="localhost",  # Dirección del servidor de base de datos
            user="root",       # Usuario de la base de datos
            password="Matkus2107",  # Contraseña de la base de datos
            database="1w"      # Nombre de la base de datos
        )
        if connection.is_connected():
            return connection
    except Error as e:
        log_error(f"Error al conectar a MySQL: {e}")
        return None

    

    
