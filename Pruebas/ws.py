from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Ruta del driver de Chrome
driver_path = "C:/Temp/chromedriver-win64/chromedriver.exe"

# Inicializa el servicio de ChromeDriver
service = Service(driver_path)

# Inicializa el driver de Selenium
driver = webdriver.Chrome(service=service)

# Abre WhatsApp Business Web
driver.get('https://web.whatsapp.com')

# Espera hasta que el usuario escanee el código QR y se abra el chat de WhatsApp Business
print("Escanea el código QR en WhatsApp Web...")

# Espera hasta que el cuadro de búsqueda esté disponiblepip install selenium
wait = WebDriverWait(driver, 60)
search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))

# Escribe el nombre del contacto en el cuadro de búsqueda
contact_name = "Juan Manuel"  # Nombre del contacto
search_box.send_keys(contact_name)

# Espera a que se muestre el contacto en los resultados
wait.until(EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]')))

# Selecciona el contacto de la lista de resultados
contact = driver.find_element(By.XPATH, f'//span[@title="{contact_name}"]')
contact.click()

# Espera a que se cargue el chat
time.sleep(2)

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






