import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

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
        return driver
    except Exception as e:
        print(f"No se pudo conectar a la sesión existente: {e}")
        return None

# Intentar abrir una nueva sesión de Chrome
def open_new_session():
    # Inicializa el servicio de ChromeDriver
    service = Service(driver_path)

    # Opciones de Chrome para mantener la sesión
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={user_data_dir}")  # Usa la carpeta de sesión
    options.add_argument("--remote-debugging-port=9222")  # Activa el puerto para depuración remota

    # Inicializa el driver de Selenium con las opciones configuradas
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Verificar si hay una sesión activa
driver = connect_to_existing_session()

# Si no hay sesión activa, abrir una nueva
if driver is None:
    print("No se encontró una sesión activa. Abriendo una nueva sesión...")
    driver = open_new_session()
    driver.get('https://web.whatsapp.com')
    print("Esperando a que se cargue WhatsApp Web...")
    wait = WebDriverWait(driver, 60)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
    print("Sesión de WhatsApp Web cargada correctamente. No se requiere escanear el QR nuevamente.")

else:
    print("Sesión activa encontrada. Trabajando con la sesión actual.")

# Continúa con el flujo habitual del script...
# Aquí puedes continuar interactuando con WhatsApp como antes
contact_name = "1w-room1"  # Nombre del contacto a buscar

# Espera a que se muestre el cuadro de búsqueda
wait = WebDriverWait(driver, 60)
search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))

# Escribe el nombre del contacto en el cuadro de búsqueda
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

