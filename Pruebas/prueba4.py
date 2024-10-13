import imaplib
import email
from email.header import decode_header
import os
import zipfile
from PyPDF2 import PdfReader
import pandas as pd

# Conexión al servidor
imap_host = 'imap.gmail.com'  # Cambia según tu proveedor de correo
username = 'Misfacturas1w@gmail.com'
password = 'owlf klmt jtlv drhh'

mail = imaplib.IMAP4_SSL(imap_host)
mail.login(username, password)
mail.select('inbox')  # Selecciona la bandeja de entrada

# Lista para almacenar los datos que se exportarán a Excel
data = []

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
                                        
                                        # Agregar los datos a la lista
                                        data.append([asunto, remitente, fecha, text])

# Convertir la lista de datos a un DataFrame de pandas
df = pd.DataFrame(data, columns=["Asunto", "Remitente", "Fecha", "Contenido PDF"])

# Exportar el DataFrame a un archivo Excel
df.to_excel("C:\\temp\\facturas.xlsx", index=False)

# Cerrar la conexión al servidor de correo
mail.close()
mail.logout()
