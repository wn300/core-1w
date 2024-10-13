import imaplib
import email
from email.header import decode_header
import os
import zipfile
import pdfplumber
import pandas as pd
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

# Conexión al servidor
imap_host = 'imap.gmail.com'  # Cambia según tu proveedor de correo
username = 'Misfacturas1w@gmail.com'
password = 'owlf klmt jtlv drhh'

mail = imaplib.IMAP4_SSL(imap_host)
mail.login(username, password)
mail.select('inbox')  # Selecciona la bandeja de entrada

# Listas para almacenar los datos extraídos
pdf_data = []
xml_data = []

# URL base para la descarga de PDFs
base_url = "https://catalogo-vpfe.dian.gov.co"

# Buscar los correos
typ, data = mail.search(None, 'ALL')

# Verificar si hay correos encontrados
if data[0]:
    # Decodificar los resultados de la búsqueda
    for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822)')
        
        # Verificar si los datos del correo son válidos
        if data and len(data) > 0:
            msg = email.message_from_bytes(data[0][1])
            
            # Verificar si el mensaje tiene partes/múltiples partes
            if msg.is_multipart():
                for part in msg.walk():
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" in content_disposition:
                        # Descargar el archivo adjunto
                        filename = part.get_filename()
                        if filename:
                            filepath = os.path.join("C:\\temp", filename)
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))

                            # Si el archivo adjunto es un ZIP, abrirlo
                            if zipfile.is_zipfile(filepath):
                                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                                    zip_ref.extractall("C:\\temp")

                                    # Procesar archivos dentro del ZIP
                                    for file in zip_ref.namelist():
                                        file_path = os.path.join("C:\\temp", file)

                                        # Si es un PDF, leer el contenido
                                        if file.endswith('.pdf'):
                                            with pdfplumber.open(file_path) as pdf:
                                                text = ""
                                                for page in pdf.pages:
                                                    text += page.extract_text() or ""
                                                pdf_data.append([msg['Subject'], msg['From'], msg['Date'], text])

                                        # Si es un XML, procesar el contenido y extraer el CUFE
                                        elif file.endswith('.xml'):
                                            tree = ET.parse(file_path)
                                            root = tree.getroot()
                                            xml_content = []
                                            for elem in root.iter():
                                                xml_content.append(f"{elem.tag}: {elem.text}")
                                            xml_content_str = "; ".join(xml_content)

                                            # Buscar el CUFE en el XML
                                            xml_string = ET.tostring(root, encoding='utf8', method='xml').decode()
                                            uuid_index = xml_string.find('UUID')
                                            if uuid_index != -1:
                                                cufe_start = uuid_index + 46
                                                CUFE = xml_string[cufe_start:cufe_start + 96]
                                            else:
                                                CUFE = "UUID no encontrado"
                                            
                                            print(f"CUFE extraído: {CUFE}")

                                            # Crear el archivo Excel por CUFE siguiendo el modelo de PDF a Excel
                                            output_excel_path = f"C:\\temp\\xls_{CUFE}.xlsx"
                                            
                                            # Crear las hojas según el ModeloPDFAEXCEL
                                            df_hd = pd.DataFrame([], columns=["Campo1", "Campo2"])  # Ejemplo: Hoja HD
                                            df_de = pd.DataFrame([], columns=["Campo3", "Campo4"])  # Ejemplo: Hoja DE
                                            df_da = pd.DataFrame([], columns=["Campo5", "Campo6"])  # Ejemplo: Hoja DA
                                            df_li = pd.DataFrame([], columns=["Campo7", "Campo8"])  # Ejemplo: Hoja LI
                                            df_it = pd.DataFrame([], columns=["Campo9", "Campo10"])  # Ejemplo: Hoja IT
                                            
                                            # Crear el archivo Excel y guardar las hojas
                                            with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
                                                df_hd.to_excel(writer, sheet_name="HD", index=False)
                                                df_de.to_excel(writer, sheet_name="DE", index=False)
                                                df_da.to_excel(writer, sheet_name="DA", index=False)
                                                df_li.to_excel(writer, sheet_name="LI", index=False)
                                                df_it.to_excel(writer, sheet_name="IT", index=False)

                                            print(f"Archivo Excel guardado en: {output_excel_path}")

# Cerrar la conexión al servidor de correo
mail.close()
mail.logout()
