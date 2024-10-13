from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Ruta al chromedriver y opciones de Chrome
CHROME_DRIVER_PATH = r"C:\Temp\chromedriver-win64\chromedriver.exe"
USER_DATA_DIR = r"C:/1wdoc/AccessoWS/WhatsApp_Session"
DEBUGGER_URL = "http://127.0.0.1:9222"  # URL para verificar la conexión con Chrome
RUTA_CHAT = "C:/1wdoc/wstxt/chat.txt"  # Ruta del archivo donde se guardarán los mensajes

# Inicializar el controlador de Chrome conectándose a la sesión existente
def init_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # Conectar a la sesión existente
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Conectado a la sesión existente de Chrome.")
    return driver

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
        except Exception:
            continue
    return "<No se encontró texto en el mensaje>"  # Retornar este valor si ningún selector encontró texto

# Función para extraer mensajes de un contacto específico en WhatsApp Web
def extraer_mensajes_whatsapp_contacto(driver, contact_name, ruta_chat):
    try:
        # Esperar a que se cargue la lista de chats
        wait = WebDriverWait(driver, 20)

        # Buscar el cuadro de búsqueda en WhatsApp y asegurarse de que esté visible e interactuable
        search_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@role="textbox"]')))
        search_box.clear()
        search_box.send_keys(contact_name)
        time.sleep(2)  # Espera para que aparezcan los resultados

        # Esperar a que el contacto se muestre y sea clicable
        contact = wait.until(EC.element_to_be_clickable((By.XPATH, f'//span[@title="{contact_name}"]')))
        contact.click()

        # Esperar a que se carguen todos los mensajes en el chat (entrantes y salientes)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')))

        # Extraer los mensajes visibles en la pantalla (entrantes y salientes)
        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')

        # Abrir el archivo en modo escritura
        with open(ruta_chat, 'w', encoding='utf-8') as file:
            # Iterar a través de los mensajes y extraer el texto usando la función `extract_message_text`
            for message in messages:
                try:
                    message_text = extract_message_text(message)
                    print(f"Mensaje: {message_text}")  # Imprimir cada mensaje capturado
                    file.write(message_text + '\n')  # Guardar cada mensaje en una línea del .txt
                except Exception as e:
                    print(f"Error al extraer el mensaje: {e}")
        print(f"Mensajes extraídos y guardados en {ruta_chat}.")
    except Exception as e:
        print(f"Error al extraer mensajes de WhatsApp Web: {e}")

# Conectar a la sesión existente de Chrome en el puerto 9222
driver = init_driver()

# Si la sesión de Chrome está activa, proceder a cargar el chat de WhatsApp Web y extraer los mensajes
try:
    # Abre WhatsApp Web
    driver.get("https://web.whatsapp.com")
    print("Sesión activa detectada en WhatsApp Web.")
    
    # Esperar para asegurarse de que el chat esté cargado
    time.sleep(5)
    
    # Escribe el nombre del contacto en el cuadro de búsqueda y extrae mensajes
    contact_name = "Juan Manuel"  # Nombre del contacto a buscar
    extraer_mensajes_whatsapp_contacto(driver, contact_name, RUTA_CHAT)

    # Verificar el contenido del archivo después de guardar
    print("Contenido del archivo .txt después de extraer mensajes:")
    with open(RUTA_CHAT, 'r', encoding='utf-8') as file:
        for i, linea in enumerate(file.readlines()):
            print(f"Línea {i+1}: {linea.strip()}")

except Exception as e:
    print(f"Error al cargar WhatsApp Web: {e}")
finally:
    # Finaliza la sesión (opcional) y cierra el script
    driver.quit()
    print("Sesión finalizada y script cerrado.")
