# main.py


import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))



import mysql.connector
from modules.cc_email_handler import conectar_servidor, procesar_correo
from modules.aa_logger import log_error


# Conexión a la base de datos MySQL
def obtener_credenciales():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Matkus2107",
            database="1w"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT correo, password FROM user WHERE id_user = '1W'")
        resultado = cursor.fetchone()
        if resultado:
            correo, password = resultado
            return correo, password
        else:
            log_error("No se encontraron credenciales para el usuario 1W.")
            return None, None

    except mysql.connector.Error as err:
        log_error(f"Error al conectar a MySQL: {err}")
        return None, None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    # Obtener credenciales del correo
    correo, password = obtener_credenciales()
    if not correo or not password:
        log_error("No se pudieron obtener las credenciales del correo.")
        return

    # Conectar al servidor de correo
    imap_host = 'imap.gmail.com'
    mail = conectar_servidor(imap_host, correo, password)

    if mail:
        try:
            mail.select('inbox')  # Selecciona la bandeja de entrada

            # Buscar los correos no leídos
            typ, data = mail.search(None, 'UNSEEN')

            if data[0]:
                for num in data[0].split():
                    typ, data = mail.fetch(num, '(RFC822)')
                    if data and len(data) > 0:
                        msg = email.message_from_bytes(data[0][1])
                        procesar_correo(msg, num)
        except Exception as e:
            log_error(f"Error inesperado: {e}")
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass  # Ignorar errores en el cierre de la conexión

if __name__ == "__main__":
    main()



