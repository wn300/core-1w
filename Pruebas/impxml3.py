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
def find_due_date_in_cdata():
    description_element = root.find('.//cbc:Description', namespaces)
    if description_element is not None and description_element.text:
        try:
            # Parsear el contenido del CDATA como un nuevo XML
            embedded_tree = ET.fromstring(description_element.text)
            due_date = embedded_tree.find('.//cbc:DueDate', namespaces)
            return due_date.text if due_date is not None else "<no disponible>"
        except ET.ParseError:
            return "<error en el CDATA>"
    return "<no disponible>"

# Extraer los campos
VXML = {
   "CUFE": find_element('.//cbc:UUID'),
    "InvoiceID": find_element('.//cbc:ID'),
    "DueDate": find_due_date_in_cdata(),  # Extraer el DueDate desde el CDATA
    "DocumentCurrencyCode": find_element('.//cbc:DocumentCurrencyCode'),
    "SupplierName": find_element('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name'),
    # Agregar otros campos si es necesario
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

