import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Ruta del driver de Chrome
driver_path = "C:/Temp/chromedriver-win64/chromedriver.exe"


# Función para conectarse a una sesión manualmente abierta de Chrome
def connect_to_existing_session():
    try:
        # Conectarse a la sesión manualmente abierta en el puerto 9222
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        print("Sesión activa encontrada. Trabajando con la sesión actual.")
        return driver
    except Exception as e:
        print(f"No se pudo conectar a la sesión existente: {e}")
        return None



# Conectarse a la sesión manualmente abierta en el puerto 9222
driver = connect_to_existing_session()

# Si no hay sesión activa, mostrar un mensaje y salir
if driver is None:
    print("No se encontró una sesión activa. Por favor, inicia Chrome manualmente con la siguiente línea:")
    print("chrome.exe --remote-debugging-port=9222 --user-data-dir='C:/1wdoc/AccessoWS/WhatsApp_Session'")
    exit()  # Salir del script, ya que no hay una sesión activa








# Esperar a que se cargue WhatsApp Web (cuadro de búsqueda)
wait = WebDriverWait(driver, 120)  # Aumentar el tiempo de espera
try:
    # Esperar a que el cuadro de búsqueda esté disponible
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
    print("Sesión de WhatsApp Web cargada correctamente.")
except TimeoutException as te:
    print(f"TimeoutException: No se encontró el cuadro de búsqueda dentro del tiempo esperado: {te}")
    print(driver.page_source)  # Muestra el contenido de la página para depurar
except Exception as e:
    print(f"Error durante la carga de WhatsApp Web: {e}")

# Continúa con el flujo habitual del script
try:
    # Esperar a que se muestre el cuadro de búsqueda
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

    print("La sesión se mantendrá abierta para futuras interacciones.")

except TimeoutException:
    print("La página de WhatsApp no se cargó completamente.")
except Exception as e:
    print(f"Error durante la interacción con WhatsApp Web: {e}")
