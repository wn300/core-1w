
# lectura de los xlm 04_import_xml


import xml.etree.ElementTree as ET
import os
import shutil

# Ruta base
base_path = r'C:\1wdoc\adjuntos'

# Espacios de nombres utilizados en el XML
namespaces = {
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
}

# Función para encontrar un elemento en el XML principal
def find_element(root, xpath):
    element = root.find(xpath, namespaces)
    return element.text if element is not None else "<no disponible>"


# Función para encontrar el CUFE, buscando primero en UUID con schemeName="CUFE-SHA384" y luego en UUID sin atributo
def find_cufe(root):
    # Buscar el CUFE con schemeName="CUFE-SHA384"
    cufe = find_element(root, './/cbc:UUID[@schemeName="CUFE-SHA384"]')
    
    # Si no lo encuentra, busca en cualquier UUID sin el atributo schemeName
    if cufe == "<no disponible>":
        cufe = find_element(root, './/cbc:UUID')
    
    return cufe



# Función para parsear el contenido dentro de CDATA
def find_in_cdata(root, xpath):
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



# Función para extraer productos
def extract_products(root, line_count):
    description_element = root.find('.//cbc:Description', namespaces)
    products = []
    if description_element is not None and description_element.text:
        try:
            # Parsear el contenido del CDATA como un nuevo XML
            embedded_tree = ET.fromstring(description_element.text)
            for i in range(1, line_count + 1):
                product_description = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:Item/cbc:Description', namespaces)
                product_quantity = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cbc:InvoicedQuantity', namespaces)
                product_line_extension = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cbc:LineExtensionAmount', namespaces)
                
                product_data = {
                    "Description": product_description.text if product_description is not None else "<no disponible>",
                    "Quantity": product_quantity.text if product_quantity is not None else "<no disponible>",
                    "LineExtensionAmount": product_line_extension.text if product_line_extension is not None else "<no disponible>"
                }
                products.append(product_data)
        except ET.ParseError:
            return "<error en el CDATA>"
    return products

# Función para procesar cada archivo XML
def process_xml(xml_path, output_txt_path):
    # Cargar el XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extraer los 17 campos, incluyendo LineCountNumeric
    VXML = {
        "CUFE": find_cufe(root),  # Buscar CUFE con lógica condicional
        "InvoiceID": find_element(root, './/cbc:ParentDocumentID'),
        "IssueDate": find_in_cdata(root, './/cbc:IssueDate'),
        "IssueTime": find_in_cdata(root, './/cbc:IssueTime'),
        "DueDate": find_in_cdata(root, './/cbc:DueDate'),  
        "DocumentCurrencyCode": find_in_cdata(root, './/cbc:DocumentCurrencyCode'),  
        "SupplierName": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name'),
        "SupplierNIT": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
        "SupplierAddress": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line'),
        "CustomerName": find_in_cdata(root, './/cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name'),
        "CustomerID": find_in_cdata(root, './/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
        "CustomerAddress": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line'),
        "PayableAmount": find_in_cdata(root, './/cac:LegalMonetaryTotal/cbc:PayableAmount'),
        "LineCountNumeric": find_in_cdata(root, './/cbc:LineCountNumeric')
    }

    # Extraer productos basados en LineCountNumeric
    line_count = int(VXML["LineCountNumeric"]) if VXML["LineCountNumeric"] != "<no disponible>" else 0
    products = extract_products(root, line_count)

    # Crear el archivo TXT con los datos extraídos
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for key, value in VXML.items():
            f.write(f"{key}: {value}\n")
        f.write("\nProductos:\n")
        for idx, product in enumerate(products, 1):
            f.write(f"Product {idx}: {product}\n")
    
    return VXML["CUFE"]

# Función para procesar las carpetas
def process_folders(base_path):
    # Contar las carpetas en el directorio base
    folders = [f.path for f in os.scandir(base_path) if f.is_dir()]
    print(f"Encontradas {len(folders)} carpetas.")
    
    for folder in folders:
        # Buscar archivo XML dentro de la carpeta
        xml_files = [f for f in os.listdir(folder) if f.endswith('.xml')]
        if not xml_files:
            print(f"No se encontró ningún archivo XML en {folder}")
            continue
        
        xml_path = os.path.join(folder, xml_files[0])
        output_txt_path = os.path.join(folder, 'VXML_data.txt')
        
        # Procesar el archivo XML y obtener el CUFE
        cufe = process_xml(xml_path, output_txt_path)
        print(f"Procesado archivo {xml_files[0]} en {folder}, CUFE: {cufe}")
        

        # Renombrar la carpeta desde el carácter 19 con el CUFE
        if cufe != "<no disponible>":
            new_folder_name = folder[:18] + cufe
            new_folder_path = os.path.join(base_path, new_folder_name)
            try:
                shutil.move(folder, new_folder_path)
                print(f"Carpeta renombrada a {new_folder_name}")
            except Exception as e:
                print(f"Error al renombrar la carpeta {folder}: {e}")
        else:
            print(f"CUFE no encontrado para el archivo {xml_files[0]}, la carpeta no será renombrada.")



# Ejecutar el procesamiento
process_folders(base_path)