import xml.etree.ElementTree as ET
import os

# Ruta del archivo XML
xml_file = r'c:\1wdoc\ad09005910380002400159524.xml'

# Cargar y parsear el XML
tree = ET.parse(xml_file)
root = tree.getroot()

# Espacios de nombres utilizados en el XML
namespaces = {
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
}

# Función para obtener texto con comprobación de existencia
def get_text_or_default(element, default="<no disponible>"):
    return element.text if element is not None else default

# Intentar extraer CUFE, si no está, buscar CUDE
cufe = get_text_or_default(root.find('cbc:UUID[@schemeName="CUFE-SHA384"]', namespaces), None)
if cufe is None:  # Si CUFE no está presente, buscar CUDE
    cufe = get_text_or_default(root.find('cbc:UUID[@schemeName="CUDE-SHA384"]', namespaces), "<no disponible>")

# Otros valores clave del XML
document_id = get_text_or_default(root.find('cbc:ID', namespaces))
issue_date = get_text_or_default(root.find('cbc:IssueDate', namespaces))
issue_time = get_text_or_default(root.find('cbc:IssueTime', namespaces))
currency_code = get_text_or_default(root.find('cbc:DocumentCurrencyCode', namespaces))

# Información del proveedor
supplier_name = get_text_or_default(root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name', namespaces))
supplier_nit = get_text_or_default(root.find('.//cac:AccountingSupplierParty/cac:PartyTaxScheme/cbc:CompanyID', namespaces))
supplier_address = get_text_or_default(root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line', namespaces))

# Información del cliente
customer_name = get_text_or_default(root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name', namespaces))
customer_nit = get_text_or_default(root.find('.//cac:AccountingCustomerParty/cac:PartyTaxScheme/cbc:CompanyID', namespaces))
customer_address = get_text_or_default(root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line', namespaces))

# Totales
total_amount = get_text_or_default(root.find('.//cac:LegalMonetaryTotal/cbc:PayableAmount', namespaces))

# Crear el contenido para el archivo txt
txt_content = f"""CUFE/CUDE: {cufe}
Número de Documento: {document_id}
Fecha de emisión: {issue_date}
Hora de emisión: {issue_time}
Moneda: {currency_code}

--- Información del Proveedor ---
Nombre: {supplier_name}
NIT: {supplier_nit}
Dirección: {supplier_address}

--- Información del Cliente ---
Nombre: {customer_name}
NIT: {customer_nit}
Dirección: {customer_address}

--- Totales ---
Monto a pagar: {total_amount} COP
"""

# Definir la ruta para guardar el archivo
output_dir = r'c:\1wdoc'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Verificar que el CUFE/CUDE sea un valor válido para el nombre del archivo
if cufe == "<no disponible>":
    file_name = "DIANTXT_default.txt"
else:
    # Reemplazar caracteres no permitidos en el nombre del archivo
    sanitized_cufe = cufe.replace("/", "_").replace("\\", "_")
    file_name = f"DIANTXT_{sanitized_cufe}.txt"

output_file = os.path.join(output_dir, file_name)

# Guardar el archivo txt con el nombre DIANTXT + CUFE o CUDE
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(txt_content)

# Imprimir los campos y valores extraídos
print(f"CUFE/CUDE: {cufe}")
print(f"Número de Nota Crédito: {document_id}")
print(f"Fecha de emisión: {issue_date}")
print(f"Hora de emisión: {issue_time}")
print(f"Moneda: {currency_code}")
print("\n--- Información del Proveedor ---")
print(f"Nombre: {supplier_name}")
print(f"NIT: {supplier_nit}")
print(f"Dirección: {supplier_address}")
print("\n--- Información del Cliente ---")
print(f"Nombre: {customer_name}")
print(f"NIT: {customer_nit}")
print(f"Dirección: {customer_address}")
print("\n--- Totales ---")
print(f"Monto a pagar: {total_amount} COP")

print(f"Archivo generado exitosamente en: {output_file}")









