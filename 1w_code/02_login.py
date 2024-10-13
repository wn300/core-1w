
# Identificaacion credenciales del usuario 02_login


import mysql.connector


# Conexión a la base de datos MySQL con la ruta especificada
def obtener_credenciales():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Matkus2107",
            database="1w",
            unix_socket="c:/1wdoc/bd/mysql.sock"  # Ruta al socket de MySQL si es necesario
        )

        cursor = connection.cursor()
        cursor.execute("SELECT imap_host, username, password FROM users WHERE id_user = '10001'")
        resultado = cursor.fetchone()
        if resultado:
            imap, username, password = resultado
            return imap, username, password
        else:
            log_error("No se encontraron credenciales para el usuario 1W.")
            return None, None, None

    except mysql.connector.Error as err:
        log_error(f"Error al conectar a MySQL: {err}")
        return None, None, None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Ejemplo de uso
imap, username, password = obtener_credenciales()
if imap and username and password:
    print(f"IMAP: {imap}, Correo: {username}, Contraseña: {password}")
else:
    print("No se pudieron obtener las credenciales")



