# modules/ee_pdf_processor.py

import sys
import os
import pdfplumber
from modules.aa_logger import log_info, log_error

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PDFProcessor:
    def __init__(self):
        pass

    @staticmethod
    def procesar_pdf(file_path, email_id):
        """Extrae el contenido de un archivo PDF y realiza el procesamiento necesario."""
        extracted_text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                # Recorre todas las páginas del PDF y extrae el texto
                for page_number, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text
                        log_info(f"Texto extraído de la página {page_number} del PDF: {file_path}")
                    else:
                        log_error(f"No se encontró texto en la página {page_number} del PDF: {file_path}")
            
            # Después de extraer el texto, intenta extraer el CUFE
            cufe = PDFProcessor.extract_cufe(extracted_text)
            if cufe:
                log_info(f"CUFE extraído del PDF {file_path}: {cufe}")
            else:
                log_error(f"CUFE no encontrado en el PDF {file_path}")
                
            # Puedes agregar aquí más lógica de procesamiento si es necesario
            return extracted_text
        except Exception as e:
            log_error(f"Error al procesar el PDF {file_path}: {e}")
            return None

    @staticmethod
    def extract_cufe(text):
        """Extrae el CUFE del texto del PDF. (Este es un ejemplo simple y debe ser ajustado según el formato del PDF)."""
        try:
            # Buscar el CUFE dentro del texto extraído (esto debe adaptarse según el formato del PDF)
            cufe_start = text.find('CUFE: ')
            if cufe_start != -1:
                cufe = text[cufe_start + 6:cufe_start + 102]  # Extrae el CUFE (por ejemplo, 96 caracteres)
                log_info(f"CUFE extraído: {cufe}")
                return cufe
            else:
                log_error("CUFE no encontrado en el PDF.")
                return None
        except Exception as e:
            log_error(f"Error al extraer el CUFE del texto del PDF: {e}")
            return None



