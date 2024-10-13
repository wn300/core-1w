import os

# Definir la estructura del proyecto
estructura = {
    "1w_project": {
        "config": ["settings.py", "database.py"],
        "modules": {
            "invoice_processor": ["xml_processor.py", "pdf_processor.py"],
            "email_handler.py": None,
            "user_management.py": None,
            "whatsapp.py": None,
        },
        "nlp": ["nlp_model.py"],
        "reports": ["report_generator.py"],
        "logs": ["logger.py"],
        "main.py": None,
        "requirements.txt": None
    }
}

# Función recursiva para crear las carpetas y archivos
def crear_estructura(base_path, estructura):
    for nombre, contenido in estructura.items():
        # Crear la carpeta o archivo
        path = os.path.join(base_path, nombre)
        if isinstance(contenido, dict):
            # Es una carpeta, crearla
            os.makedirs(path, exist_ok=True)
            # Crear los subelementos
            crear_estructura(path, contenido)
        elif isinstance(contenido, list):
            # Crear la carpeta
            os.makedirs(path, exist_ok=True)
            # Crear los archivos dentro de la carpeta
            for archivo in contenido:
                archivo_path = os.path.join(path, archivo)
                open(archivo_path, 'w').close()  # Crear archivo vacío
        else:
            # Crear archivo en el directorio base
            open(path, 'w').close()

# Directorio base
base_path = os.getcwd()  # Cambiar si quieres otro directorio base

# Crear la estructura
crear_estructura(base_path, estructura)

print("Estructura del proyecto generada correctamente.")
