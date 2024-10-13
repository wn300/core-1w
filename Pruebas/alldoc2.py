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
import re
from datetime import datetime

# Conexión al servidor
imap_host = 'imap.gmail.com'  # Cambia según tu proveedor de correo
username = 'Misfacturas1w@gmail.com'
password = 'owlf klmt jtlv drhh'

# Directorios
base_dir = r"C:\1wdoc\adjuntos"
log_dir = r"C:\1wdoc"
os.makedirs(base_dir, exist_ok=True)

# Nombre del archivo de log con fecha y hora
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(log_dir, f"log_{current_time}.txt")

# URL base para la descarga de PDFs
base_url = "https://catalogo-vpfe.dian.gov.co"

def log_error(message):
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def procesar_correo(msg, num):
    try:
        # Crear una carpeta específica para este correo basada en su ID único de Gmail
        email_id = num.decode()
        subject = decode_header(msg['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        # Limpiar el nombre de la carpeta eliminando caracteres no válidos y truncando
        subject_cleaned = re.sub(r'[<>:"/\\|?*\r\n;]', '_', subject)
        subject_cleaned = subject_cleaned[:50]  # Limitar a 50 caracteres
        folder_name = f"IDMLDOC{email_id.zfill(10)}_{subject_cleaned}"
        email_dir = os.path.join(base_dir, folder_name)

        try:
            os.makedirs(email_dir, exist_ok=True)
        except OSError as e:
            log_error(f"Error al crear la carpeta {email_dir}: {e}")
            return  # Termina la función si hay un error al crear la carpeta

        # Guardar una copia del correo en un archivo de texto
        guardar_correo_texto(msg, email_dir, email_id)

        # Procesar los archivos adjuntos
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" in content_disposition:
                    procesar_adjunto(part, email_dir, email_id)
    except Exception as e:
        log_error(f"Error procesando el correo {num.decode()}: {e}")

def guardar_correo_texto(msg, email_dir, email_id):
    try:
        email_text_path = os.path.join(email_dir, "email.txt")
        with open(email_text_path, "w", encoding="utf-8") as email_file:
            email_file.write(f"From: {msg['From']}\n")
            email_file.write(f"Subject: {msg['Subject']}\n")
            email_file.write(f"Date: {msg['Date']}\n")
            email_file.write(f"\n{msg.as_string()}")
    except Exception as e:
        log_error(f"Error al guardar el correo {email_id}: {e}")

def procesar_adjunto(part, email_dir, email_id):
    try:
        filename = part.get_filename()
        if filename:
            filepath = os.path.join(email_dir, filename)
            try:
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
            except Exception as e:
                log_error(f"Error al guardar el archivo adjunto {filename} en {email_id}: {e}")
                return

            # Si el archivo adjunto es un ZIP, abrirlo
            if zipfile.is_zipfile(filepath):
                procesar_zip(filepath, email_dir, email_id)
    except Exception as e:
        log_error(f"Error al procesar el adjunto en {email_id}: {e}")

def procesar_zip(filepath, email_dir, email_id):
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(email_dir)
            for file in zip_ref.namelist():
                file_path = os.path.join(email_dir, file)
                if file.endswith('.pdf'):
                    procesar_pdf(file_path, email_id)
                elif file.endswith('.xml'):
                    procesar_xml(file_path, email_dir, email_id)
    except Exception as e:
        log_error(f"Error al extraer el archivo ZIP {filepath} en {email_id}: {e}")

def procesar_pdf(file_path, email_id):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            pdf_data.append([msg['Subject'], msg['From'], msg['Date'], text])
    except pdfminer.pdfdocument.PDFPasswordIncorrect:
        log_error(f"El PDF {file_path} está protegido con contraseña y no se puede abrir en {email_id}.")
    except Exception as e:
        log_error(f"Error al procesar el PDF {file_path} en {email_id}: {e}")



                        # Función para procesar los archivos XML
                        def procesar_xml(file_path, email_dir, email_id):
                            try:
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

                                # Extraer los campos del XML, incluyendo los productos
                                campos_xml = extraer_campos_xml(root)

                                # Acceder al HTML y descargar el PDF
                                descargar_pdf_dian(CUFE, email_dir, email_id)

                                # Crear el archivo Excel por CUFE
                                crear_excel(CUFE, email_dir, email_id)

                                # Crear el archivo TXT por CUFE con los campos extraídos
                                crear_txt(CUFE, campos_xml, xml_content_str, email_dir, email_id)

                            except Exception as e:
                                log_error(f"Error al procesar el XML {file_path} en {email_id}: {e}")


                                # Espacios de nombres utilizados en el XML
                                namespaces = {
                                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
                                    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
                                }

                                # Función para encontrar un elemento en el XML principal
                                def find_element(xpath):
                                    element = root.find(xpath, namespaces)
                                    return element.text if element is not None else "<no disponible>"

                                # Función para parsear el contenido dentro de CDATA
                                def find_in_cdata(xpath):
                                    description_element = root.find('.//cbc:Description', namespaces)
                                    if description_element is not None and description_element.text:
                                        try:
                                            # Parsear el contenido del CDATA como un nuevo XML
                                            embedded_tree = ET.fromstring(description_element.text)
                                            element = embedded_tree.find(xpath, namespaces)
                                            return element.text if element is not None else "<no disponible>"
                                        except ET.ParseError:
                                            return "<error en el CDATA>"
                                    return "<no disponible>"

                                # Función para extraer productos
                                def extract_products(line_count):
                                    description_element = root.find('.//cbc:Description', namespaces)
                                    products = []
                                    if description_element is not None and description_element.text:
                                        try:
                                            # Parsear el contenido del CDATA como un nuevo XML
                                            embedded_tree = ET.fromstring(description_element.text)
                                            for i in range(1, line_count + 1):
                                                product_description = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:Item/cbc:Description', namespaces)
                                                product_quantity = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cbc:InvoicedQuantity', namespaces)
                                                product_line_extension = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cbc:LineExtensionAmount', namespaces)
                                                
                                                product_data = {
                                                    "Description": product_description.text if product_description is not None else "<no disponible>",
                                                    "Quantity": product_quantity.text if product_quantity is not None else "<no disponible>",
                                                    "LineExtensionAmount": product_line_extension.text if product_line_extension is not None else "<no disponible>"
                                                }
                                                products.append(product_data)
                                        except ET.ParseError:
                                            return "<error en el CDATA>"
                                    return products

                            
                            # Extraer los 17 campos, incluyendo LineCountNumeric
                            VXML = {
                                "CUFE": find_element('.//cbc:UUID'),
                                "InvoiceID": find_element('.//cbc:ParentDocumentID'),
                                "IssueDate": find_in_cdata('.//cbc:IssueDate'),
                                "IssueTime": find_in_cdata('.//cbc:IssueTime'),
                                "DueDate": find_in_cdata('.//cbc:DueDate'),  
                                "DocumentCurrencyCode": find_in_cdata('.//cbc:DocumentCurrencyCode'),  
                                "SupplierName": find_in_cdata('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name'),
                                "SupplierNIT": find_in_cdata('.//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
                                "SupplierAddress": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line'),
                                "CustomerName": find_in_cdata('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name'),
                                "CustomerID": find_in_cdata('.//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
                                "CustomerAddress": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line'),
                                "PayableAmount": find_in_cdata('.//cac:LegalMonetaryTotal/cbc:PayableAmount'),
                                "LineCountNumeric": find_in_cdata('.//cbc:LineCountNumeric')
                            }

                            # Extraer productos basados en LineCountNumeric
                            line_count = int(VXML["LineCountNumeric"]) if VXML["LineCountNumeric"] != "<no disponible>" else 0
                            products = extract_products(line_count)



                        # Función para crear el archivo TXT por CUFE
                        def crear_txt(CUFE, campos_xml, xml_content_str, email_dir, email_id):
                            try:
                                txt_filename = f"XLMTXT{CUFE}.txt"
                                txt_file_path = os.path.join(email_dir, txt_filename)
                                with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                                    txt_file.write(f"CUFE: {CUFE}\n")
                                    txt_file.write("Campos extraídos del XML:\n")
                                    for key, value in campos_xml.items():
                                        if key != "Productos":  # Excluye la lista de productos en este bucle
                                            txt_file.write(f"{key}: {value}\n")
                                    
                                    # Escribir los detalles de los productos
                                    txt_file.write("\nProductos:\n")
                                    for idx, producto in enumerate(campos_xml["Productos"], 1):
                                        txt_file.write(f"Producto {idx}: Descripción: {producto['Description']}, Cantidad: {producto['Quantity']}, Monto: {producto['LineExtensionAmount']}\n")
                                    
                                print(f"Archivo TXT creado: {txt_file_path}")
                            except Exception as e:
                                log_error(f"Error al crear el archivo TXT para CUFE {CUFE} en {email_id}: {e}")




def descargar_pdf_dian(CUFE, email_dir, email_id):
    try:
        html_url = f"https://catalogo-vpfe.dian.gov.co/Document/searchqr?Documentkey={CUFE}"
        response = requests.get(html_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar el token y descargar el PDF
        links = soup.find_all('a', href=True)
        for link in links:
            if 'token=' in link['href']:
                token_start = link['href'].find('token=') + len('token=')
                token = link['href'][token_start:token_start + 64]
                pdf_url = f"/Document/DownloadPDF?trackId={CUFE}&token={token}"
                full_pdf_url = base_url + pdf_url

                # Descargar el PDF
                try:
                    pdf_response = requests.get(full_pdf_url, stream=True, timeout=10)
                    pdf_response.raise_for_status()
                    output_path = os.path.join(email_dir, f"DIAN_{CUFE}.pdf")
                    with open(output_path, 'wb') as f:
                        f.write(pdf_response.content)
                except requests.exceptions.RequestException as e:
                    log_error(f"Error al descargar PDF para CUFE {CUFE} en {email_id}: {e}")
    except requests.exceptions.RequestException as e:
        log_error(f"Error al acceder a la URL del HTML para CUFE {CUFE} en {email_id}: {e}")

def crear_excel(CUFE, email_dir, email_id):
    try:
        output_excel_path = os.path.join(email_dir, f"xls_{CUFE}.xlsx")
        df_pdf = pd.DataFrame(pdf_data, columns=["Asunto", "Remitente", "Fecha", "Contenido PDF"])
        df_xml = pd.DataFrame(xml_data, columns=["Asunto", "Remitente", "Fecha", "Contenido XML", "CUFE"])
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            df_pdf.to_excel(writer, sheet_name="PDFs", index=False)
            df_xml.to_excel(writer, sheet_name="XMLs", index=False)
    except Exception as e:
        log_error(f"Error al crear el archivo Excel para CUFE {CUFE} en {email_id}: {e}")

def main():
    try:
        # Establecer la conexión con el servidor de correo
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(username, password)
        mail.select('inbox')  # Selecciona la bandeja de entrada

        # Buscar los correos no leídos
        typ, data = mail.search(None, 'UNSEEN')

        if data[0]:
            for num in data[0].split():
                typ, data = mail.fetch(num, '(RFC822)')
                if data and len(data) > 0:
                    msg = email.message_from_bytes(data[0][1])
                    procesar_correo(msg, num)
    except Exception as e:
        log_error(f"Error inesperado: {e}")
    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass  # Ignorar errores en el cierre de la conexión

if __name__ == "__main__":
    main()