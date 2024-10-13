import requests

# Base URL
base_url = "https://catalogo-vpfe.dian.gov.co"

# URL del PDF a descargar (extraída del href en el enlace de descarga)
pdf_url = "/Document/DownloadPDF?trackId=e0208feb24fafcf3c21cb333ea4c051f024e1db6dff30cce8acff906d98a1f58aa7b3641349eab10e8d496ac01aacf96&token=397ac6707dd8bafaf439e3824c6de12d0353ff46b39638b4d501bda55fa3d41b"

# Extraer los últimos 96 caracteres de la URL para usar como nombre de archivo
document_key = pdf_url[-96:]  # Esto asume que el pdf_url tiene al menos 96 caracteres

# URL completa
full_url = base_url + pdf_url

# Realizar la solicitud GET para descargar el archivo PDF
response = requests.get(full_url, stream=True)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Ruta donde se guardará el PDF, utilizando el `document_key` como nombre
    output_path = f"C:\\temp\\{document_key}.pdf"

    # Guardar el contenido en un archivo
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"PDF descargado y guardado en {output_path}")
else:
    print("Error al descargar el PDF:", response.status_code)


