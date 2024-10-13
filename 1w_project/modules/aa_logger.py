import logging
import os

# Configuración del directorio de logs
log_dir = "C:\\1wdoc\\logs"  # Cambia esta ruta si es necesario
os.makedirs(log_dir, exist_ok=True)  # Crear el directorio si no existe
log_file = os.path.join(log_dir, "app.log")

# Configuración del logger
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def log_info(message):
    """
    Registra un mensaje de información en el archivo de log.
    """
    logging.info(message)

def log_error(message):
    """
    Registra un mensaje de error en el archivo de log.
    """
    logging.error(message)
