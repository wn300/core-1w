from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def connect_to_existing_session():
    """Conecta a la sesión de Chrome existente."""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # Conectar a la sesión de Chrome existente en el puerto 9222
    
    try:
        # Intentar conectarse a la sesión de Chrome existente
        driver = webdriver.Chrome(options=chrome_options)
        print("Conectado a la sesión existente de Chrome.")
        return driver
    except Exception as e:
        print(f"Error al conectar con la sesión existente de Chrome: {e}")
        return None

def debug_chat_structure(driver):
    """Recorre y muestra todos los elementos de texto en el chat abierto para encontrar la estructura."""
    try:
        print("Depurando la estructura del chat abierto...")

        # Buscar todos los `div` y `span` dentro del chat
        chat_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]//div | //div[contains(@class, "message-in") or contains(@class, "message-out")]//span')
        
        # Mostrar la cantidad de elementos encontrados
        print(f"Cantidad de elementos encontrados dentro del chat: {len(chat_elements)}")

        # Mostrar el contenido de cada elemento
        for index, element in enumerate(chat_elements):
            try:
                # Imprimir el índice del elemento y el texto
                print(f"Elemento {index + 1}: {element.text.strip()}")
            except Exception as e:
                print(f"Error al leer el contenido de un elemento: {e}")

    except Exception as e:
        print(f"Error al depurar la estructura del chat: {e}")

if __name__ == "__main__":
    # Conectar a la sesión existente de Chrome
    driver = connect_to_existing_session()

    # Si la conexión es exitosa, depurar la estructura del chat
    if driver:
        print("Depurando la estructura del chat abierto para encontrar la estructura de los mensajes...")
        debug_chat_structure(driver)
    else:
        print("No se pudo conectar a la sesión existente de Chrome.")















