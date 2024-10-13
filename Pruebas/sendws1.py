

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
from selenium.webdriver import ActionChains

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



    # Nombre del contacto y mensaje que se va a enviar
    contact_name = "1w-room1"
    mensaje = "Hola soy 1W, desde este momento estoy conectado con este grupo para ayudar en el procesamiento de tus transacciones"

    try:
        # Esperar a que el cuadro de búsqueda esté disponible y buscar el contacto
        wait = WebDriverWait(driver, 30)
        search_bar = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
        
        # Limpiar el cuadro de búsqueda y escribir el nombre del contacto
        search_bar.clear()
        search_bar.send_keys(contact_name)
        time.sleep(2)  # Esperar para que se muestren los resultados de búsqueda

        # Verificar los resultados de búsqueda y hacer clic en el contacto usando JavaScript
        contact_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]')))
        driver.execute_script("arguments[0].click();", contact_element)
        print(f"Contacto {contact_name} encontrado y seleccionado correctamente.")
        time.sleep(2)  # Esperar a que se abra el chat

        # Enviar TAB 10 veces para llegar al cuadro de mensajes
        print("Enviando 10 TAB para llegar al cuadro de mensaje...")
        search_bar.send_keys(Keys.TAB * 10)
        time.sleep(2)  # Esperar un momento para asegurarse de que está en el cuadro de mensaje

        # Usar ActionChains para hacer clic en el cuadro de mensaje y escribir el mensaje
        action = ActionChains(driver)
        action.send_keys(mensaje).perform()  # Escribir el mensaje
        action.send_keys(Keys.ENTER).perform()  # Enviar el mensaje
        print(f"Mensaje enviado a {contact_name}: {mensaje}")
    except Exception as e:
        print(f"No se pudo enviar el mensaje a {contact_name}: {e}")
    finally:
        # Esperar un momento antes de cerrar
        time.sleep(3)

    # No cerrar el navegador para futuras interacciones
    # driver.quit()






    # Dejar la sesión abierta para continuar trabajando en ella
    print("La sesión se mantendrá abierta para futuras interacciones.")

except Exception as e:
    print(f"Error durante la interacción con WhatsApp Web: {e}")

# Elimina el cierre de sesión al final, dejando la sesión abierta
# driver.quit()  # Comentado para mantener la sesión abierta