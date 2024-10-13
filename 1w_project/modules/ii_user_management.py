# modules/ii_user_management.py

import sys
import os

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import connect_db
from modules.aa_logger import log_info, log_error

class UserManager:
    def __init__(self):
        # Establecer la conexión a la base de datos
        self.connection = connect_db()
    
    def get_user_credentials(self, user_name):
        """Obtiene las credenciales de un usuario específico desde la base de datos."""
        try:
            if not self.connection:
                log_error("No se pudo establecer la conexión con la base de datos.")
                return None

            query = "SELECT * FROM users WHERE name_user = %s"

            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (user_name,))
            user = cursor.fetchone()
            cursor.close()

            if user:
                log_info(f"Credenciales obtenidas para el usuario: {user_name}")
                return {
                    'imap_host': user.get('imap_host'),
                    'imap_user': user.get('username'),
                    'imap_password': user.get('password')
                }
            else:
                log_error(f"Usuario no encontrado: {user_name}")
                return None
        except Exception as e:
            log_error(f"Error al obtener las credenciales del usuario {user_name}: {e}")
            return None

    def close_connection(self):
        """Cierra la conexión a la base de datos."""
        try:
            if self.connection.is_connected():
                self.connection.close()
                log_info("Conexión con la base de datos cerrada correctamente.")
        except Exception as e:
            log_error(f"Error al cerrar la conexión con la base de datos: {e}")





