

#Funciona abriendo manual mente "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/1wdoc/AccessoWS/WhatsApp_Session"


import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Ruta del driver de Chrome y la carpeta de sesión
driver_path = "C:/Temp/chromedriver-win64/chromedriver.exe"
user_data_dir = r"C:/1wdoc/AccessoWS/WhatsApp_Session"

# Si la carpeta de sesión no existe, crearla
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

# Intentar conectarse a una sesión abierta de Chrome
def connect_to_existing_session():
    try:
        # Conectarse a una sesión ya existente si está abierta
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        print("Sesión activa encontrada. Trabajando con la sesión actual.")
        return driver
    except Exception as e:
        print(f"No se pudo conectar a la sesión existente: {e}")
        return None

# Iniciar una nueva sesión de Chrome con modo de depuración
def start_chrome_with_debugging():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # Usar la carpeta de sesión
    chrome_options.add_argument("--remote-debugging-port=9222")  # Activar modo depuración en el puerto 9222

    # Iniciar Chrome con el servicio de ChromeDriver
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    print("Nueva sesión de Chrome abierta con el modo de depuración.")
    return driver


# Intentar conectar a una sesión existente
def connect_to_existing_session():
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        print("Sesión activa encontrada. Trabajando con la sesión actual.")
        return driver
    except Exception as e:
        print(f"No se pudo conectar a la sesión existente: {e}")
        return None

# Conectar a la sesión existente o abrir una nueva
driver = connect_to_existing_session()
if driver is None:
    print("No se encontró una sesión activa. Abriendo una nueva sesión en modo depuración...")
    driver = start_chrome_with_debugging()

# Intentar cargar WhatsApp Web
try:
    driver.get('https://web.whatsapp.com')
    time.sleep(5)  # Esperar 5 segundos para ver si la página carga
    print("Intentando cargar WhatsApp Web...")

    # Verificar el título de la página para asegurar que se cargó correctamente
    if "WhatsApp" in driver.title:
        print("WhatsApp Web cargado correctamente.")
    else:
        print(f"No se pudo cargar WhatsApp Web. Título de la página actual: {driver.title}")

except Exception as e:
    print(f"Error durante la carga de WhatsApp Web: {e}")


# Continúa con el flujo habitual del script si se carga correctamente
try:
    # Esperar a que se muestre el cuadro de búsqueda
    wait = WebDriverWait(driver, 120)  # Aumentar el tiempo de espera
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))

    # Escribe el nombre del contacto en el cuadro de búsqueda
    contact_name = "1w-room1"  # Nombre del contacto
    search_box.send_keys(contact_name)

    # Espera a que se muestre el contacto en los resultados y seleccionarlo
    wait.until(EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]')))
    contact = driver.find_element(By.XPATH, f'//span[@title="{contact_name}"]')
    contact.click()

    # Espera a que se cargue el chat
    time.sleep(2)

    # Espera a que se carguen todos los mensajes en el chat (entrantes y salientes)
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')))
    messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')

    # Función para intentar diferentes selectores y capturar el texto del mensaje
    def extract_message_text(message):
        selectors = [
            './/span[contains(@class, "selectable-text")]',  # Selector original para mensajes de texto
            './/div[@aria-label]',  # Selector alternativo para mensajes con aria-label
            './/div[contains(@class, "copyable-text")]',  # Selector para mensajes reenviados o estructurados
            './/div[contains(@class, "_ahyv")]',  # Selector alternativo visto en la estructura del mensaje
        ]
        
        for selector in selectors:
            try:
                element = message.find_element(By.XPATH, selector)
                if element.text.strip():  # Verificar que el elemento tenga texto
                    return element.text
            except NoSuchElementException:
                continue
        return "<No se encontró texto en el mensaje>"  # Retornar este valor si ningún selector encontró texto

    # Iterar a través de los mensajes y extraer el texto usando la función
    for message in messages:
        try:
            message_text = extract_message_text(message)
            print(f"Mensaje: {message_text}")
        except Exception as e:
            print(f"Error al extraer el mensaje: {e}")

    # Dejar la sesión abierta para continuar trabajando en ella
    print("La sesión se mantendrá abierta para futuras interacciones.")

except Exception as e:
    print(f"Error durante la interacción con WhatsApp Web: {e}")

# Elimina el cierre de sesión al final, dejando la sesión abierta
# driver.quit()  # Comentado para mantener la sesión abierta
