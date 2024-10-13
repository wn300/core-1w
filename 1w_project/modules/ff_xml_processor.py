# modules/ff_xml_processor.py

import sys
import os
import xml.etree.ElementTree as ET

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.aa_logger import log_info, log_error

class XMLProcessor:
    def __init__(self):
        pass

    def process_xml(self, file_path):
        """Procesa un archivo XML y extrae su contenido."""
        try:
            # Analiza el archivo XML
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Convierte el contenido del XML en una cadena
            xml_content = ET.tostring(root, encoding='utf8', method='xml').decode()
            log_info(f"XML procesado correctamente: {file_path}")
            return xml_content
        except ET.ParseError as e:
            log_error(f"Error al analizar el XML {file_path}: {e}")
            return None
        except Exception as e:
            log_error(f"Error al procesar el XML {file_path}: {e}")
            return None

    def extract_cufe(self, xml_content):
        """Extrae el CUFE de un XML."""
        try:
            # Encuentra el CUFE dentro del contenido del XML
            # Ajusta este método según la estructura específica de tu XML
            uuid_index = xml_content.find('UUID')
            if uuid_index != -1:
                cufe_start = uuid_index + 46  # Ajusta este valor según la estructura del XML
                cufe = xml_content[cufe_start:cufe_start + 96]  # Supone que el CUFE tiene 96 caracteres
                log_info(f"CUFE extraído: {cufe}")
                return cufe
            else:
                log_error("CUFE no encontrado en el XML.")
                return None
        except Exception as e:
            log_error(f"Error al extraer el CUFE del XML: {e}")
            return None















