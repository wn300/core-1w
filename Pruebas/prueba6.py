import imaplib
import email
from email.header import decode_header
import os
import zipfile
from PyPDF2 import PdfReader
import pandas as pd
import xml.etree.ElementTree as ET
import tempfile

# Conexión al servidor
imap_host = 'imap.gmail.com'  # Cambia según tu proveedor de correo
username = 'Misfacturas1w@gmail.com'
password = 'owlf klmt jtlv drhh'

mail = imaplib.IMAP4_SSL(imap_host)
mail.login(username, password)
mail.select('inbox')  # Selecciona la bandeja de entrada

# Listas para almacenar los datos que se exportarán a Excel
pdf_data = []
xml_data = []

# Buscar los últimos 5 correos
typ, email_ids = mail.search(None, 'ALL')

# Decodificar los resultados de la búsqueda
for num in email_ids[0].split():
    typ, data_email = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(data_email[0][1])
    
    asunto = msg['Subject']
    remitente = msg['From']
    fecha = msg['Date']
    
    # Verificar si el mensaje tiene partes/múltiples partes
    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                # Descargar el archivo adjunto
                filename = part.get_filename()
                if filename:
                    # Usar un directorio temporal para almacenar los archivos
                    with tempfile.TemporaryDirectory() as temp_dir:
                        filepath = os.path.join(temp_dir, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        
                        # Si el archivo adjunto es un ZIP, abrirlo
                        if zipfile.is_zipfile(filepath):
                            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                                zip_ref.extractall(temp_dir)

                                # Procesar archivos dentro del ZIP
                                for file in zip_ref.namelist():
                                    file_path = os.path.join(temp_dir, file)

                                    # Si es un PDF, leer y extraer contenido
                                    if file.endswith('.pdf'):
                                        try:
                                            with open(file_path, 'rb') as pdf_file:
                                                pdf_reader = PdfReader(pdf_file)
                                                page = pdf_reader.pages[0]
                                                text = page.extract_text()
                                                print(f"Contenido del PDF '{file}':\n{text}")
                                                
                                                # Agregar los datos a la lista de PDF
                                                pdf_data.append([asunto, remitente, fecha, text])
                                        except Exception as e:
                                            print(f"Error al leer PDF {file}: {e}")

                                    # Si es un XML, leer y procesar contenido
                                    elif file.endswith('.xml'):
                                        try:
                                            tree = ET.parse(file_path)
                                            root = tree.getroot()

                                            # Unificar nodos (por ejemplo, concatenar texto de nodos relevantes)
                                            xml_content = []
                                            for elem in root.iter():
                                                xml_content.append(f"{elem.tag}: {elem.text}")
                                            
                                            xml_content_str = "; ".join(xml_content)
                                            print(f"Contenido del XML '{file}':\n{xml_content_str}")

                                            # Agregar los datos a la lista de XML
                                            xml_data.append([asunto, remitente, fecha, xml_content_str])
                                        except Exception as e:
                                            print(f"Error al leer XML {file}: {e}")

# Convertir las listas de datos a DataFrames de pandas
df_pdf = pd.DataFrame(pdf_data, columns=["Asunto", "Remitente", "Fecha", "Contenido PDF"])
df_xml = pd.DataFrame(xml_data, columns=["Asunto", "Remitente", "Fecha", "Contenido XML"])

# Exportar los DataFrames a un archivo Excel en dos hojas
output_file = os.path.join("C:\\temp", "facturas.xlsx")
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df_pdf.to_excel(writer, sheet_name="PDFs", index=False)
    df_xml.to_excel(writer, sheet_name="XMLs", index=False)

print(f"Archivo Excel guardado en: {output_file}")

# Cerrar la conexión al servidor de correo
mail.close()
mail.logout()
