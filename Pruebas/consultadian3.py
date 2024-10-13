import requests
import os

# URL del PDF a descargar
url = "https://catalogo-vpfe.dian.gov.co/Document/DownloadPDF?trackld=0820028cee297b2fc8932277fa23942720bd6331e34c5ecdb89f557fbefa88872411764463ab774c1f4e2c13682f2b93"

# Extraer los últimos 96 caracteres del `Documentkey` de la URL para usar como nombre de archivo
document_key = url.split('Documentkey=')[-1][-96:]

# Ruta donde se guardará el PDF, utilizando el `Documentkey` como nombre
output_path = os.path.join("C:\\temp", f"{document_key}.pdf")

# Realizar la solicitud GET para descargar el archivo
#response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Guardar el contenido en un archivo
    with open(output_path, 'wb') as file:
        file.write(response.content)
    print(f"PDF descargado y guardado en {output_path}")
else:
    print("Error al descargar el PDF:", response.status_code)