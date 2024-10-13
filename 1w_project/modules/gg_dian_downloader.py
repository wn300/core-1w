# modules/gg_dian_downloader.py

import sys
import os
import requests
from bs4 import BeautifulSoup

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.aa_logger import log_info, log_error

class DIANDownloader:
    def __init__(self, base_url, download_dir):
        self.base_url = base_url
        self.download_dir = download_dir

    def download_pdf(self, cufe):
        """Descarga el PDF desde la DIAN usando el CUFE proporcionado."""
        try:
            # Construir la URL para acceder al HTML de la DIAN
            html_url = f"{self.base_url}/Document/searchqr?Documentkey={cufe}"
            response = requests.get(html_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar el token en el HTML
            token = self._extract_token(soup)
            if not token:
                log_error(f"Token no encontrado para el CUFE {cufe}")
                return None

            # Construir la URL para descargar el PDF
            pdf_url = f"{self.base_url}/Document/DownloadPDF?trackId={cufe}&token={token}"
            pdf_response = requests.get(pdf_url, stream=True, timeout=10)
            pdf_response.raise_for_status()

            # Guardar el PDF en el directorio de descargas
            pdf_path = f"{self.download_dir}/DIAN_{cufe}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_response.content)
            
            log_info(f"PDF descargado correctamente para el CUFE {cufe}: {pdf_path}")
            return pdf_path
        except requests.exceptions.RequestException as e:
            log_error(f"Error al acceder a la URL de la DIAN para el CUFE {cufe}: {e}")
            return None
        except Exception as e:
            log_error(f"Error al descargar el PDF para el CUFE {cufe}: {e}")
            return None

    def _extract_token(self, soup):
        """Extrae el token necesario para la descarga del PDF desde el HTML."""
        try:
            links = soup.find_all('a', href=True)
            for link in links:
                if 'token=' in link['href']:
                    token_start = link['href'].find('token=') + len('token=')
                    token = link['href'][token_start:token_start + 64]  # Asumiendo que el token tiene 64 caracteres
                    log_info(f"Token extraído: {token}")
                    return token
            return None
        except Exception as e:
            log_error(f"Error al extraer el token del HTML: {e}")
            return None










