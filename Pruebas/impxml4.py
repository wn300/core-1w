import xml.etree.ElementTree as ET
import os

# Ruta del archivo XML
xml_path = r'C:\1wdoc\ad09005910380002400159524.xml'
output_txt_path = r'C:\1wdoc\VXML_data.txt'

# Cargar el XML
tree = ET.parse(xml_path)
root = tree.getroot()

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

# Extraer los campos desde el principal y desde el CDATA
VXML = {
    "CUFE": find_element('.//cbc:UUID'),
    "InvoiceID": find_element('.//cbc:ID'),
    "DueDate": find_in_cdata('.//cbc:DueDate'),  # Extraer desde el CDATA
    "DocumentCurrencyCode": find_in_cdata('.//cbc:DocumentCurrencyCode'),  # Extraer desde el CDATA
    "SupplierName": find_in_cdata('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name')  # Extraer desde el CDATA
}

# Imprimir el resultado
for key, value in VXML.items():
    print(f"{key}: {value}")

# Crear el directorio si no existe
os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)

# Guardar los datos en un archivo txt
with open(output_txt_path, 'w', encoding='utf-8') as f:
    for key, value in VXML.items():
        f.write(f"{key}: {value}\n")

print(f"Datos guardados en {output_txt_path}")
