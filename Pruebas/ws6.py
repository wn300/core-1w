from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import os
import time

# Ruta del driver de Chrome
driver_path = "C:/Temp/chromedriver-win64/chromedriver.exe"

# Ruta para guardar la sesión de usuario en C:/Temp
user_data_dir = r"C:/1wdoc/AccessoWS/WhatsApp_Session"

# Si la carpeta no existe, crearla
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

# Inicializa el servicio de ChromeDriver
service = Service(driver_path)

# Opciones de Chrome para mantener la sesión
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={user_data_dir}")  # Usa la carpeta de sesión

# Inicializa el driver de Selenium con las opciones configuradas
driver = webdriver.Chrome(service=service, options=options)

# Abre WhatsApp Business Web
driver.get('https://web.whatsapp.com')

# Espera hasta que se cargue la interfaz de WhatsApp Web
print("Esperando a que se cargue WhatsApp Web...")

# Espera hasta que el cuadro de búsqueda esté disponible
wait = WebDriverWait(driver, 60)
search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))

print("Sesión de WhatsApp Web cargada correctamente. No se requiere escanear el QR nuevamente.")

# Realiza tus operaciones de WhatsApp, como seleccionar contactos, enviar mensajes, etc.
# Aquí un ejemplo de cómo seleccionar un contacto y mostrar mensajes:

# Escribe el nombre del contacto en el cuadro de búsqueda
contact_name = "1w-room1"  # Nombre del contacto
search_box.send_keys(contact_name)

# Espera a que se muestre el contacto en los resultados
wait.until(EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]')))

# Selecciona el contacto de la lista de resultados
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

# Aquí puedes agregar la lógica para responder o realizar alguna acción con los mensajes

# Finaliza la sesión (opcional)
driver.quit()
