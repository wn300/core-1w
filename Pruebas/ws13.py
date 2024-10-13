from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests  # Biblioteca para verificar la conexión al puerto 9222
import time

# Ruta al chromedriver y opciones de Chrome
CHROME_DRIVER_PATH = r"C:\Temp\chromedriver-win64\chromedriver.exe"
USER_DATA_DIR = r"C:/1wdoc/AccessoWS/WhatsApp_Session"
DEBUGGER_URL = "http://127.0.0.1:9222"  # URL para verificar la conexión con Chrome

def is_chrome_running():
    """Verifica si la sesión de Chrome está ejecutándose en el puerto 9222."""
    try:
        response = requests.get(f"{DEBUGGER_URL}/json")
        if response.status_code == 200 and len(response.json()) > 0:
            print("Conectado a la sesión existente de Chrome.")
            return True
        else:
            print(f"No se pudo conectar a Chrome: {response.status_code}")
            return False
    except Exception as e:
        print(f"No se pudo conectar a Chrome: {e}")
        return False

def init_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # Conectar a sesión existente

    # Intentar conectarse a la sesión existente utilizando la URL de WebSocket
    if is_chrome_running():
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("Conectado a la sesión existente de Chrome.")
            return driver
        except Exception as e:
            print(f"Error al conectar con la sesión existente de Chrome: {e}")
            driver = None
    else:
        print("No se encontró una sesión existente de Chrome o no se pudo conectar.")
        driver = None

    # Si no se pudo conectar a la sesión existente, iniciar una nueva sesión de Chrome
    if not driver:
        print("Iniciando una nueva sesión de Chrome.")
        chrome_options.add_argument(f"--remote-debugging-port=9222")
        chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        service = Service(CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Nueva sesión de Chrome iniciada.")

    return driver

if __name__ == "__main__":
    # Conectar a la sesión existente de Chrome en el puerto 9222 o iniciar una nueva
    driver = init_driver()

    # Verificar si la sesión está activa
    if driver:
        try:
            driver.get("https://web.whatsapp.com")
            print("Sesión activa detectada en WhatsApp Web.")
            
            # Mantener el script corriendo indefinidamente para que la sesión no se cierre
            print("El script se mantendrá ejecutándose para mantener la sesión abierta.")
            while True:
                time.sleep(10)  # Esperar indefinidamente para mantener la sesión abierta
        except Exception as e:
            print(f"Error al cargar WhatsApp Web: {e}")
    else:
        print("No se pudo iniciar sesión en Chrome. Verifica que la sesión esté disponible.")
