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

# Función para encontrar un elemento en el XML
def find_element(xpath):
    element = root.find(xpath, namespaces)
    return element.text if element is not None else "<no disponible>"

# Extraer los 16 campos
VXML = {
    "CUFE": find_element('.//cbc:UUID'),
    "InvoiceID": find_element('.//cbc:ID'),
    "IssueDate": find_element('.//cbc:IssueDate'),
    "IssueTime": find_element('.//cbc:IssueTime'),
    "DueDate": find_element('.//cbc:DueDate'),
    "DocumentCurrencyCode": find_element('.//cbc:DocumentCurrencyCode'),
    "SupplierName": find_element('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name'),
    "SupplierNIT": find_element('.//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
    "SupplierAddress": find_element('.//cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:Line'),
    "CustomerName": find_element('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name'),
    "CustomerID": find_element('.//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
    "CustomerAddress": find_element('.//cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:Line'),
    "PayableAmount": find_element('.//cac:LegalMonetaryTotal/cbc:PayableAmount'),
    "Product1Description": find_element('.//cac:InvoiceLine[1]/cac:Item/cbc:Description'),
    "Product1Quantity": find_element('.//cac:InvoiceLine[1]/cbc:InvoicedQuantity'),
    "Product1LineExtensionAmount": find_element('.//cac:InvoiceLine[1]/cbc:LineExtensionAmount')
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
