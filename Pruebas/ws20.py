

#Funciona abriendo manual mente "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/1wdoc/AccessoWS/WhatsApp_Session"


import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys


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
    driver.get('https://web.whatsapp.com')
    print("Esperando a que se cargue WhatsApp Web...")
    return driver

# Verificar si hay una sesión activa
driver = connect_to_existing_session()

# Si no hay sesión activa, abrir una nueva
if driver is None:
    print("No se encontró una sesión activa. Abriendo una nueva sesión...")
    driver = open_new_session()
    wait = WebDriverWait(driver, 120)  # Aumentar el tiempo de espera
    try:
        # Esperar a que el cuadro de búsqueda esté disponible
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
        print("Sesión de WhatsApp Web cargada correctamente. No se requiere escanear el QR nuevamente.")
    except TimeoutException as te:
        print(f"TimeoutException: No se encontró el cuadro de búsqueda dentro del tiempo esperado: {te}")
        print(driver.page_source)  # Muestra el contenido de la página para depurar
else:
    print("Sesión activa encontrada. Trabajando con la sesión actual.")

# Continúa con el flujo habitual del script si se carga correctamente
try:
    # Esperar a que se muestre el cuadro de búsqueda
    wait = WebDriverWait(driver, 120)  # Aumentar el tiempo de espera

    search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))


    # Limpia el cuadro de búsqueda usando diferentes métodos
    search_box.click()  # Asegúrate de que el cuadro de búsqueda esté seleccionado
    search_box.send_keys(Keys.CONTROL + "a")  # Selecciona todo el texto existente
    search_box.send_keys(Keys.DELETE)  # Elimina el texto seleccionado

    # Asegúrate de que el cuadro de búsqueda esté vacío antes de escribir el nuevo contacto
    time.sleep(1)  # Espera para asegurar que el texto se haya eliminado

    # Escribe el nombre del contacto en el cuadro de búsqueda
    contact_name = "Juan Manuel"  # Nombre del contacto
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



    # Función para extraer el texto, fecha, hora y nombre del usuario que envía cada mensaje
    def extract_message_details(message):
        try:
            # Intentar extraer el nombre y fecha/hora del mensaje desde el atributo `data-pre-plain-text`
            user_info_element = message.find_element(By.XPATH, './/div[@data-pre-plain-text]')
            pre_plain_text = user_info_element.get_attribute("data-pre-plain-text")

            # Validar que `pre_plain_text` no sea None
            if pre_plain_text:
                # Extraer la fecha y hora
                datetime_info = pre_plain_text.split("]")[0].replace("[", "")  # Extrae la fecha y la hora
                user_name = pre_plain_text.split("]")[1].strip(": ")  # Extrae el nombre del usuario sin el carácter ':'
            else:
                # Si no se encuentra el atributo `data-pre-plain-text`, asignar valores predeterminados
                datetime_info = "<Fecha y hora no disponibles>"
                user_name = "<Usuario no disponible>"

            # Extraer el texto del mensaje utilizando la función anterior
            message_text = extract_message_text(message)
            
            # Formato de salida: Fecha, Hora, Usuario, Mensaje
            formatted_message = f"{datetime_info} | {user_name} : {message_text}"
            return formatted_message

        except NoSuchElementException:
            return "<No se encontró información completa del mensaje>"
        except AttributeError:
            # Capturar casos en los que `split` falla porque `pre_plain_text` es None
            return "<No se pudo extraer detalles del mensaje>"

    # Iterar a través de los mensajes y extraer los detalles usando la nueva función
    for message in messages:
        try:
            message_details = extract_message_details(message)
            print(f"Mensaje Detallado: {message_details}")
        except Exception as e:
            print(f"Error al extraer detalles del mensaje: {e}")








    # Dejar la sesión abierta para continuar trabajando en ella
    print("La sesión se mantendrá abierta para futuras interacciones.")

except Exception as e:
    print(f"Error durante la interacción con WhatsApp Web: {e}")

# Elimina el cierre de sesión al final, dejando la sesión abierta
# driver.quit()  # Comentado para mantener la sesión abierta
