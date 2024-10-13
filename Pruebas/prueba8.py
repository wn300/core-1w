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

                                            # Construir la URL para acceder al HTML
                                            html_url = f"https://catalogo-vpfe.dian.gov.co/Document/searchqr?Documentkey={CUFE}"
                                            print(f"Accediendo a la URL del HTML: {html_url}")

                                            # Obtener el HTML
                                            response = requests.get(html_url)
                                            if response.status_code == 200:
                                                soup = BeautifulSoup(response.content, 'html.parser')

                                                # Imprimir el HTML para verificar su estructura
                                                print("HTML obtenido:\n", soup.prettify()[:500])  # Solo mostrar una parte del HTML

                                                # Buscar todos los enlaces para verificar si el token está presente
                                                links = soup.find_all('a', href=True)
                                                found_token = False
                                                for link in links:
                                                    if 'token=' in link['href']:
                                                        found_token = True
                                                        token_start = link['href'].find('token=') + len('token=')
                                                        token = link['href'][token_start:token_start + 64]
                                                        pdf_url = f"/Document/DownloadPDF?trackId={CUFE}&token={token}"
                                                        
                                                        # Descargar el PDF
                                                        full_pdf_url = base_url + pdf_url
                                                        pdf_response = requests.get(full_pdf_url, stream=True)
                                                        
                                                        if pdf_response.status_code == 200:
                                                            output_path = f"C:\\temp\\DIAN_{CUFE}.pdf"
                                                            with open(output_path, 'wb') as f:
                                                                f.write(pdf_response.content)
                                                            print(f"PDF descargado y guardado en {output_path}")
                                                        else:
                                                            print(f"Error al descargar PDF para CUFE {CUFE}: {pdf_response.status_code}")
                                                        break
                                                if not found_token:
                                                    print(f"No se encontró el token en el HTML para CUFE {CUFE}")
                                            else:
                                                token = "Error al acceder al HTML"
                                                print(f"Error al acceder al HTML para CUFE {CUFE}: {response.status_code}")

                                            # Agregar los datos del XML, CUFE y token a la lista
                                            xml_data.append([msg['Subject'], msg['From'], msg['Date'], xml_content_str, CUFE, "Token no encontrado"])

# Convertir los datos extraídos a DataFrames de pandas
df_pdf = pd.DataFrame(pdf_data, columns=["Asunto", "Remitente", "Fecha", "Contenido PDF"])
df_xml = pd.DataFrame(xml_data, columns=["Asunto", "Remitente", "Fecha", "Contenido XML", "CUFE", "Token"])

# Exportar los DataFrames a un archivo Excel con dos hojas
output_file = "C:\\temp\\facturas.xlsx"
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df_pdf.to_excel(writer, sheet_name="PDFs", index=False)
    df_xml.to_excel(writer, sheet_name="XMLs", index=False)

print(f"Archivo Excel guardado en: {output_file}")

# Cerrar la conexión al servidor de correo
mail.close()
mail.logout()


  
