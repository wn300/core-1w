import imaplib
import email
from email.header import decode_header
import os
import zipfile
import pdfplumber

# Conexión al servidor
imap_host = 'imap.gmail.com'  # Cambia según tu proveedor de correo
username = 'Misfacturas1w@gmail.com'
password = 'owlf klmt jtlv drhh'

mail = imaplib.IMAP4_SSL(imap_host)
mail.login(username, password)
mail.select('inbox')  # Selecciona la bandeja de entrada

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

                                    # Buscar archivos PDF dentro del ZIP y leerlos
                                    for file in zip_ref.namelist():
                                        if file.endswith('.pdf'):
                                            pdf_path = os.path.join("C:\\temp", file)
                                            # Intentar leer el PDF usando pdfplumber
                                            try:
                                                with pdfplumber.open(pdf_path) as pdf:
                                                    for page in pdf.pages:
                                                        text = page.extract_text()
                                                        if text:
                                                            print(f"Contenido del PDF '{file}':\n{text}")
                                                        else:
                                                            print(f"No se pudo extraer texto del PDF '{file}'")
                                            except Exception as e:
                                                print(f"Error al leer el PDF {file}: {e}")
            # Mostrar información del correo
            print('Asunto:', msg['Subject'])
            print('De:', msg['From'])
            print('Fecha:', msg['Date'])
            print('-------------------')

else:
    print("No se encontraron correos.")

mail.close()
mail.logout()





