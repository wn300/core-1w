# modules/hh_excel_generator.py

import sys
import os
import pandas as pd

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.aa_logger import log_info, log_error

class ExcelGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generate_excel(self, pdf_data, xml_data, cufe):
        """Genera un archivo Excel a partir de los datos extraídos del PDF y del XML."""
        try:
            # Crear un DataFrame para los datos del PDF
            pdf_df = pd.DataFrame(pdf_data, columns=["Página", "Contenido"])
            
            # Crear un DataFrame para los datos del XML
            xml_df = pd.DataFrame(xml_data, columns=["Etiqueta", "Valor"])
            
            # Definir el nombre del archivo Excel
            excel_filename = f"{self.output_dir}/Factura_{cufe}.xlsx"
            
            # Escribir los datos en el archivo Excel en hojas separadas
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                pdf_df.to_excel(writer, sheet_name='Datos_PDF', index=False)
                xml_df.to_excel(writer, sheet_name='Datos_XML', index=False)
            
            log_info(f"Archivo Excel generado correctamente: {excel_filename}")
            return excel_filename
        except Exception as e:
            log_error(f"Error al generar el archivo Excel para CUFE {cufe}: {e}")
            return None



