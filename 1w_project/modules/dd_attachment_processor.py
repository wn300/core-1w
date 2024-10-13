# modules/dd_attachment_processor.py

import sys
import os
import re
import zipfile
from email.header import decode_header
from modules.bb_file_manager import FileManager
from modules.aa_logger import log_info, log_error
from modules.ee_pdf_processor import PDFProcessor  # Ajuste: Importar la clase

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AttachmentProcessor:
    def __init__(self, base_dir):
        # El directorio base donde se guardarán los adjuntos
        self.file_manager = FileManager(base_dir)
        self.base_dir = base_dir  # Mantener la referencia a base_dir

    def procesar_correo(self, msg, num):
        """Procesa un correo electrónico y guarda sus adjuntos en una carpeta específica."""
        try:
            # Crear una carpeta específica para este correo basada en su ID único de Gmail
            email_id = num.decode()
            subject = decode_header(msg['Subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            # Limpiar el nombre de la carpeta eliminando caracteres no válidos y truncando
            subject_cleaned = re.sub(r'[<>:"/\\|?*\r\n;]', '_', subject)
            subject_cleaned = subject_cleaned[:25]  # Limitar a 25 caracteres
            folder_name = f"IDMLDOC{email_id.zfill(10)}_{subject_cleaned}"
            email_dir = os.path.join(self.base_dir, folder_name)

            # Crear la carpeta si no existe
            try:
                os.makedirs(email_dir, exist_ok=True)
                log_info(f"Carpeta creada para el correo: {email_dir}")
            except OSError as e:
                log_error(f"Error al crear la carpeta {email_dir}: {e}")
                return  # Termina la función si hay un error al crear la carpeta

            # Guardar una copia del correo en un archivo de texto
            self.guardar_correo_texto(msg, email_dir, email_id)

            # Procesar los archivos adjuntos
            if msg.is_multipart():
                for part in msg.walk():
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" in content_disposition:
                        log_info(f"Procesando adjunto en {email_dir}")
                        self.procesar_adjunto(part, email_dir, email_id)
        except Exception as e:
            log_error(f"Error procesando el correo {num.decode()}: {e}")

    def guardar_correo_texto(self, msg, email_dir, email_id):
        """Guarda una copia del correo en un archivo de texto."""
        try:
            email_text_path = os.path.join(email_dir, "email.txt")
            with open(email_text_path, "w", encoding="utf-8") as email_file:
                email_file.write(f"From: {msg['From']}\n")
                email_file.write(f"Subject: {msg['Subject']}\n")
                email_file.write(f"Date: {msg['Date']}\n")
                email_file.write(f"\n{msg.as_string()}")
            log_info(f"Correo guardado como texto en {email_text_path}")
        except Exception as e:
            log_error(f"Error al guardar el correo {email_id}: {e}")

    def procesar_adjunto(self, part, email_dir, email_id):
        """Procesa y guarda un archivo adjunto del correo electrónico."""
        try:
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(email_dir, filename)
                try:
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    log_info(f"Archivo adjunto guardado en {filepath}")
                except Exception as e:
                    log_error(f"Error al guardar el archivo adjunto {filename} en {email_id}: {e}")
                    return

                # Si el archivo adjunto es un ZIP, abrirlo
                if zipfile.is_zipfile(filepath):
                    log_info(f"El archivo es un ZIP, procesando: {filename}")
                    self.procesar_zip(filepath, email_dir, email_id)
        except Exception as e:
            log_error(f"Error al procesar el adjunto en {email_id}: {e}")

    def procesar_zip(self, filepath, email_dir, email_id):
        """Extrae y procesa el contenido de un archivo ZIP adjunto."""
        try:
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(email_dir)
                log_info(f"Archivos extraídos del ZIP en {email_dir}")
                for file in zip_ref.namelist():
                    file_path = os.path.join(email_dir, file)
                    if file.endswith('.pdf'):
                        # Llamada al método estático
                        PDFProcessor.procesar_pdf(file_path, email_id)
                    elif file.endswith('.xml'):
                        procesar_xml(file_path, email_dir, email_id)
        except Exception as e:
            log_error(f"Error al extraer el archivo ZIP {filepath} en {email_id}: {e}")














