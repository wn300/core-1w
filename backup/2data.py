import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # Usuario predeterminado
        password="Matkus2107",  # Clave de acceso
        database="1w"  # Nombre de la base de datos
    )
