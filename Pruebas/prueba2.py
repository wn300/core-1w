import imaplib
import email
from email.header import decode_header
import os
import zipfile
from PyPDF2 import PdfReader

# Conexión al servidor
imap_host = 'imap.gmail.com'  # Cambia según tu proveedor de correo
username = 'Misfacturas1w@gmail.com'
password = 'owlf klmt jtlv drhh'

mail = imaplib.IMAP4_SSL(imap_host)
mail.login(username, password)
mail.select('inbox')  # Selecciona la bandeja de entrada

# Buscar los últimos 5 correos
typ, data = mail.search(None, 'ALL')

# Decodificar los resultados de la búsqueda
for num in data[0].split():
    typ, data = mail.fetch(num, '(RFC822)')
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
                                    with open(pdf_path, 'rb') as pdf_file:
                                        pdf_reader = PdfReader(pdf_file)
                                        # Leer el contenido del PDF (por ejemplo, la primera página)
                                        page = pdf_reader.pages[0]
                                        text = page.extract_text()
                                        print(f"Contenido del PDF '{file}':\n{text}")

    print('Asunto:', msg['Subject'])
    print('De:', msg['From'])
    print('Fecha:', msg['Date'])
    print('-------------------')

mail.close()
mail.logout()
