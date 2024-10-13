# modules/bb_file_manager.py

import sys
import os
import zipfile

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.aa_logger import log_info, log_error

class FileManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def save_attachment(self, filename, attachment_data):
        """Guarda un archivo adjunto en el sistema de archivos."""
        try:
            file_path = os.path.join(self.base_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(attachment_data)
            log_info(f"Archivo adjunto guardado en: {file_path}")
            return file_path
        except Exception as e:
            log_error(f"Error al guardar el archivo adjunto {filename}: {e}")
            return None

    def is_zip(self, file_path):
        """Verifica si el archivo es un archivo ZIP."""
        return zipfile.is_zipfile(file_path)

    def extract_zip(self, zip_path):
        """Extrae un archivo ZIP y devuelve la lista de archivos extraídos."""
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.base_dir)
                extracted_files = zip_ref.namelist()
                log_info(f"Archivos extraídos de {zip_path}: {extracted_files}")
            return [os.path.join(self.base_dir, f) for f in extracted_files]
        except Exception as e:
            log_error(f"Error al extraer el archivo ZIP {zip_path}: {e}")
            return []

    def is_pdf(self, filename):
        """Verifica si un archivo es un PDF."""
        return filename.lower().endswith('.pdf')

    def is_xml(self, filename):
        """Verifica si un archivo es un XML."""
        return filename.lower().endswith('.xml')







