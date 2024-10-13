from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

contact_name = "1w-room1"  # Nombre del contacto a buscar
search_box.send_keys(contact_name)  # Escribe el nombre en el cuadro de búsqueda

# Espera a que se muestre el contacto en los resultados y haz clic en él
wait.until(EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]')))
contact = driver.find_element(By.XPATH, f'//span[@title="{contact_name}"]')
contact.click()

# Extrae los mensajes visibles en la pantalla (entrantes y salientes)
messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')

# Itera a través de los mensajes y extrae el texto
for message in messages:
    try:
        # Encuentra el primer span con el texto del mensaje, independiente de la clase
        message_text = message.find_element(By.XPATH, './/span[contains(@class, "selectable-text")]').text
        print(f"Mensaje: {message_text}")
    except Exception as e:
        print(f"Error al extraer el mensaje: {e}")

# Finaliza la sesión (opcional)
driver.quit()
