import pymysql
import re


# Función para conectar a la base de datos MySQL
def conectar_base_datos():
    try:
        conexion = pymysql.connect(
            host='localhost',
            user='root',
            password='Matkus2107',
            db='1w',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor  # Para devolver resultados como diccionarios
        )
        print("Conexión a la base de datos exitosa.")
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None




# Función para cargar las consultas SQL desde `sql_functions.txt`
def cargar_consultas_sql(archivo='c:/1wdoc/nlp/sql_functions.txt'):
    consultas_sql = {}
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            nombre_funcion = None
            consulta = []

            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue

                if ':' in linea:
                    if nombre_funcion and consulta:
                        consultas_sql[nombre_funcion] = '\n'.join(consulta)
                    
                    nombre_funcion, _ = linea.split(':', 1)
                    nombre_funcion = nombre_funcion.strip()
                    consulta = []
                else:
                    consulta.append(linea)

            if nombre_funcion and consulta:
                consultas_sql[nombre_funcion] = '\n'.join(consulta)

        print("Consultas SQL cargadas con éxito.")
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo}' no se encontró.")
    except Exception as e:
        print(f"Error al leer el archivo '{archivo}': {e}")

    return consultas_sql

# Función para cargar intenciones y asociarlas con las funciones SQL desde `dic_int.txt`
def cargar_intenciones_desde_archivo(archivo='c:/1wdoc/nlp/dic_int.txt', consultas_sql=None):
    diccionario_intenciones = {}
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue

                if ':' in linea:
                    intencion, nombre_funcion = linea.split(':', 1)
                    intencion = intencion.strip().lower()
                    nombre_funcion = nombre_funcion.strip()

                    if consultas_sql and nombre_funcion in consultas_sql:
                        diccionario_intenciones[intencion] = consultas_sql[nombre_funcion]
                    else:
                        print(f"Advertencia: La función '{nombre_funcion}' no tiene una consulta SQL definida.")
        print("Diccionario de intenciones cargado con éxito.")
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo}' no se encontró.")
    except Exception as e:
        print(f"Error al leer el archivo '{archivo}': {e}")

    return diccionario_intenciones

# Función para ejecutar la consulta SQL en la base de datos y obtener el resultado
def ejecutar_consulta(sql):
    conexion = conectar_base_datos()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql)
            resultado = cursor.fetchone()
            return list(resultado.values())[0] if resultado else 0
    finally:
        conexion.close()

# Función para interpretar el mensaje usando el diccionario de intenciones y consultas SQL
def interpretar_mensaje(mensaje, diccionario_intenciones):
    if "1w" not in mensaje.lower():
        return None

    _, mensaje = mensaje.lower().split("1w", 1)
    mensaje = mensaje.strip()
    mensaje = re.sub(r'[^\w\s]', '', mensaje)

    for clave in diccionario_intenciones:
        if all(palabra in mensaje for palabra in clave.split()):
            sql = diccionario_intenciones[clave]
            return ejecutar_consulta(sql)

    return None

# Función para almacenar la respuesta generada en la tabla `respuestas_whatsapp`
def almacenar_respuesta(mensaje_id, respuesta, idws):
    conexion = conectar_base_datos()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO respuestas_whatsapp (mensaje_id, respuesta, idws, enviado)
                VALUES (%s, %s, %s, 0);
            """, (mensaje_id, respuesta, idws))
            conexion.commit()
    finally:
        conexion.close()

# Función para leer mensajes no procesados desde la tabla `mensajes_whatsapp`
def leer_mensajes_no_procesados():
    conexion = conectar_base_datos()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id, mensaje, idws FROM mensajes_whatsapp WHERE procesado = 0;")
            mensajes = cursor.fetchall()
            print(f"Mensajes no procesados: {mensajes}")
            return mensajes
    finally:
        conexion.close()

# Función para marcar el mensaje como procesado en la tabla `mensajes_whatsapp`
def marcar_mensaje_como_procesado(mensaje_id):
    conexion = conectar_base_datos()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE mensajes_whatsapp SET procesado = 1 WHERE id = %s;", (mensaje_id,))
            conexion.commit()
    finally:
        conexion.close()

# Función principal para manejar y procesar mensajes con NLP usando el diccionario de intenciones y consultas SQL
def manejar_mensajes_whatsapp():
    print("Iniciando el proceso de manejo de mensajes...")

    consultas_sql = cargar_consultas_sql('c:/1wdoc/nlp/sql_functions.txt')
    diccionario_intenciones = cargar_intenciones_desde_archivo('c:/1wdoc/nlp/dic_int.txt', consultas_sql)

    mensajes = leer_mensajes_no_procesados()
    
    for mensaje in mensajes:
        mensaje_id = mensaje['id']
        texto_mensaje = mensaje['mensaje']
        idws = mensaje['idws']

        print(f"Procesando mensaje ID {mensaje_id} con contenido: {texto_mensaje}")

        try:
            resultado = interpretar_mensaje(texto_mensaje, diccionario_intenciones)
            print(f"Resultado de la interpretación para el mensaje ID {mensaje_id}: {resultado}")

            if resultado is not None:
                respuesta = f"El resultado de tu consulta es: {resultado}"
            else:
                respuesta = "Lo siento, no entiendo tu consulta o no contiene '1w'."

            almacenar_respuesta(mensaje_id, respuesta, idws)
            print(f"Respuesta almacenada: {respuesta}")
            marcar_mensaje_como_procesado(mensaje_id)
            print(f"Mensaje ID {mensaje_id} marcado como procesado.")
        except Exception as e:
            print(f"Error al procesar el mensaje ID {mensaje_id}: {e}")

# Ejecutar la función para manejar mensajes
manejar_mensajes_whatsapp()








