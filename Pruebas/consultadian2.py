import requests
import os

def descargar_pdf(url, ruta_descarga):
  """Descargara un PDF desde la URL especificada y lo guarda en la ruta indicada.

  Args:
    url: La URL del PDF.
    ruta_descarga: La ruta completa donde se guardará el archivo.
  """

  try:
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Levanta una excepción si el código de estado no es 200

    with open(ruta_descarga, 'wb') as f:
      for chunk in response.iter_content(chunk_size=1024):
        if chunk:
          f.write(chunk)

    print(f"Archivo descargado exitosamente en: {ruta_descarga}")

  except requests.exceptions.RequestException as e:
      print(f"Error al descargar el archivo: {e}")
  except OSError as e:
      print(f"Error al guardar el archivo: {e}")

# URL del PDF
url = "https://catalogo-vpfe.dian.gov.co/Document/searchqr?Documentkey=0820028cee297b2fc8932277fa23942720bd6331e34c5ecdb89f557fbefa88872411764463ab774c1f54e2c13682f2b93"

# Extraer los últimos 96 caracteres de la URL como nombre del archivo
nombre_archivo = url[-96:] + ".pdf"

# Ruta completa de descarga
ruta_descarga = "c:\\temp\\" + nombre_archivo

descargar_pdf(url, ruta_descarga)