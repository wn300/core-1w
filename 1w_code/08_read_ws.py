import pymysql
import pandas as pd

# Parámetros de conexión a la base de datos
db_config = {
    'host': 'localhost',           # Dirección de tu servidor MySQL
    'user': 'root',                # Usuario de MySQL
    'password': 'Matkus2107',      # Contraseña de MySQL
    'database': '1w',              # Nombre de la base de datos
    'charset': 'utf8mb4'           # Codificación para admitir caracteres especiales
}

# Ruta del archivo .txt a cargar
file_path = "C:/1wdoc/wstxt/chatroom1.txt"

# Leer el archivo .txt usando pandas y procesar cada columna
data = pd.read_csv(file_path, sep='|', header=None, names=["FechaHora", "UsuarioMensaje"], engine='python')

# Eliminar filas que no contengan información válida
data = data[data['FechaHora'].str.contains("a.m.|p.m.")]

# Separar la columna 'FechaHora' en 'Hora' y 'Fecha'
data[['Hora', 'Fecha']] = data['FechaHora'].str.split(',', expand=True)

# Separar la columna 'UsuarioMensaje' en 'idws' y 'Mensaje'
data[['idws', 'Mensaje']] = data['UsuarioMensaje'].str.split(':', n=1, expand=True)

# Eliminar columnas que no son necesarias
data = data[['Fecha', 'Hora', 'idws', 'Mensaje']]

# Reemplazar NaN con cadenas vacías
data.fillna("", inplace=True)

# Conectarse a la base de datos MySQL
connection = pymysql.connect(**db_config)

try:
    # Crear cursor para ejecutar las operaciones
    with connection.cursor() as cursor:
        # Iterar sobre cada fila del DataFrame y verificar si el registro ya existe
        for _, row in data.iterrows():
            # Consulta SQL para verificar si ya existe el registro
            sql_check = """
            SELECT COUNT(*) FROM mensajes_whatsapp
            WHERE fecha = %s AND hora = %s AND idws = %s AND mensaje = %s;
            """
            
            # Ejecutar la consulta de verificación
            cursor.execute(sql_check, (row['Fecha'].strip(), row['Hora'].strip(), row['idws'].strip(), row['Mensaje'].strip()))
            result = cursor.fetchone()
            
            # Si no existe el registro, proceder con la inserción
            if result[0] == 0:  # Si COUNT(*) = 0, no existe duplicado
                sql_insert = """
                INSERT INTO mensajes_whatsapp (fecha, hora, idws, mensaje)
                VALUES (%s, %s, %s, %s);
                """
                cursor.execute(sql_insert, (row['Fecha'].strip(), row['Hora'].strip(), row['idws'].strip(), row['Mensaje'].strip()))
                print(f"Registro insertado: {row['Fecha']} {row['Hora']} {row['idws']} - {row['Mensaje']}")
            else:
                print(f"Registro duplicado encontrado y omitido: {row['Fecha']} {row['Hora']} {row['idws']} - {row['Mensaje']}")

        # Confirmar la transacción
        connection.commit()
        print(f"Datos cargados exitosamente en la tabla 'mensajes_whatsapp' desde {file_path}")

except Exception as e:
    print(f"Error al cargar los datos en MySQL: {e}")

finally:
    # Cerrar la conexión
    connection.close()