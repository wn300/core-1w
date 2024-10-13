import xml.etree.ElementTree as ET

# Cargar y parsear el archivo XML
xml_file = r'c:\temp\ad09007770630362417002034.xml'
tree = ET.parse(xml_file)
root = tree.getroot()

# Definir todos los namespaces usados en el archivo XML
namespaces = {
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',  # Namespace 'sts'
    'ds': 'http://www.w3.org/2000/09/xmldsig#'
}

# Función para extraer el texto de un elemento, manejando el caso cuando el nodo es None
def extract_text(element, tag, namespace):
    if element is not None:
        try:
            return element.find(f'{namespace}:{tag}', namespaces).text
        except AttributeError:
            return "<no disponible>"
    return "<no disponible>"

# Información general
ubl_version = extract_text(root, 'UBLVersionID', 'cbc')
customization_id = extract_text(root, 'CustomizationID', 'cbc')
profile_id = extract_text(root, 'ProfileID', 'cbc')
invoice_id = extract_text(root, 'ID', 'cbc')

# Búsqueda del CUFE en el nodo correcto
uuid_node = root.find('.//cbc:UUID', namespaces)
uuid = uuid_node.text if uuid_node is not None else "<no disponible>"

issue_date = extract_text(root, 'IssueDate', 'cbc')
issue_time = extract_text(root, 'IssueTime', 'cbc')

# Búsqueda más profunda para el código de moneda
currency_node = root.find('.//cbc:DocumentCurrencyCode', namespaces)
document_currency_code = currency_node.text if currency_node is not None else "<no disponible>"

# Búsqueda más profunda para el número de líneas
line_count_node = root.find('.//cbc:LineCountNumeric', namespaces)
line_count_numeric = line_count_node.text if line_count_node is not None else "<no disponible>"

# Información del emisor
supplier_party = root.find('.//cac:AccountingSupplierParty', namespaces)
if supplier_party is not None:
    supplier_name = extract_text(supplier_party.find('.//cac:Party', namespaces), 'Name', 'cbc')
    supplier_id = extract_text(supplier_party.find('.//cac:PartyIdentification', namespaces), 'ID', 'cbc')
    supplier_tax_code = extract_text(supplier_party.find('.//cac:PartyTaxScheme', namespaces), 'TaxLevelCode', 'cbc')
    supplier_address = supplier_party.find('.//cac:Address', namespaces)
    supplier_city = extract_text(supplier_address, 'CityName', 'cbc')
    supplier_department = extract_text(supplier_address, 'CountrySubentity', 'cbc')
    supplier_address_line = extract_text(supplier_address.find('cac:AddressLine', namespaces), 'Line', 'cbc')
    supplier_country = extract_text(supplier_address.find('cac:Country', namespaces), 'Name', 'cbc')
else:
    supplier_name = supplier_id = supplier_tax_code = "<no disponible>"
    supplier_city = supplier_department = supplier_address_line = supplier_country = "<no disponible>"

# Información del receptor
customer_party = root.find('.//cac:AccountingCustomerParty', namespaces)
if customer_party is not None:
    customer_name = extract_text(customer_party.find('.//cac:Party', namespaces), 'Name', 'cbc')
    customer_id = extract_text(customer_party.find('.//cac:PartyIdentification', namespaces), 'ID', 'cbc')
    customer_tax_code = extract_text(customer_party.find('.//cac:PartyTaxScheme', namespaces), 'TaxLevelCode', 'cbc')
    customer_address = customer_party.find('.//cac:Address', namespaces)
    customer_city = extract_text(customer_address, 'CityName', 'cbc')
    customer_department = extract_text(customer_address, 'CountrySubentity', 'cbc')
    customer_address_line = extract_text(customer_address.find('cac:AddressLine', namespaces), 'Line', 'cbc')
    customer_country = extract_text(customer_address.find('cac:Country', namespaces), 'Name', 'cbc')
else:
    customer_name = customer_id = customer_tax_code = "<no disponible>"
    customer_city = customer_department = customer_address_line = customer_country = "<no disponible>"

# Información de la entrega
delivery = root.find('.//cac:Delivery', namespaces)
if delivery is not None:
    delivery_date = extract_text(delivery, 'ActualDeliveryDate', 'cbc')
    delivery_time = extract_text(delivery, 'ActualDeliveryTime', 'cbc')
    delivery_address = delivery.find('.//cac:Address', namespaces)
    delivery_city = extract_text(delivery_address, 'CityName', 'cbc')
    delivery_department = extract_text(delivery_address, 'CountrySubentity', 'cbc')
    delivery_address_line = extract_text(delivery_address.find('cac:AddressLine', namespaces), 'Line', 'cbc')
else:
    delivery_date = delivery_time = "<no disponible>"
    delivery_city = delivery_department = delivery_address_line = "<no disponible>"

# Información monetaria
monetary_total = root.find('.//cac:LegalMonetaryTotal', namespaces)
if monetary_total is not None:
    line_extension_amount = extract_text(monetary_total, 'LineExtensionAmount', 'cbc')
    tax_exclusive_amount = extract_text(monetary_total, 'TaxExclusiveAmount', 'cbc')
    tax_inclusive_amount = extract_text(monetary_total, 'TaxInclusiveAmount', 'cbc')
    payable_amount = extract_text(monetary_total, 'PayableAmount', 'cbc')
else:
    line_extension_amount = tax_exclusive_amount = tax_inclusive_amount = payable_amount = "<no disponible>"

# Línea de la factura
invoice_line = root.find('.//cac:InvoiceLine', namespaces)
if invoice_line is not None:
    line_id = extract_text(invoice_line, 'ID', 'cbc')
    invoiced_quantity = extract_text(invoice_line, 'InvoicedQuantity', 'cbc')
    line_extension_amount_line = extract_text(invoice_line, 'LineExtensionAmount', 'cbc')
    item_description = extract_text(invoice_line.find('cac:Item', namespaces), 'Description', 'cbc')
    item_price = extract_text(invoice_line.find('cac:Price', namespaces), 'PriceAmount', 'cbc')
else:
    line_id = invoiced_quantity = line_extension_amount_line = item_description = item_price = "<no disponible>"

# Información de validación (DIAN)
dian_extensions = root.find('.//ext:ExtensionContent/sts:DianExtensions', namespaces)
if dian_extensions is not None:
    invoice_authorization = extract_text(dian_extensions.find('sts:InvoiceControl', namespaces), 'InvoiceAuthorization', 'sts')
    start_date = extract_text(dian_extensions.find('sts:InvoiceControl/sts:AuthorizationPeriod', namespaces), 'StartDate', 'cbc')
    end_date = extract_text(dian_extensions.find('sts:InvoiceControl/sts:AuthorizationPeriod', namespaces), 'EndDate', 'cbc')
    authorized_invoices_from = extract_text(dian_extensions.find('sts:InvoiceControl/sts:AuthorizedInvoices', namespaces), 'From', 'sts')
    authorized_invoices_to = extract_text(dian_extensions.find('sts:InvoiceControl/sts:AuthorizedInvoices', namespaces), 'To', 'sts')
    security_code = extract_text(dian_extensions, 'SoftwareSecurityCode', 'sts')
    qr_code = extract_text(dian_extensions, 'QRCode', 'sts')
else:
    invoice_authorization = start_date = end_date = authorized_invoices_from = authorized_invoices_to = security_code = qr_code = "<no disponible>"

# Mostrar los datos
print(f"UBL Version: {ubl_version}")
print(f"Customization ID: {customization_id}")
print(f"Profile ID: {profile_id}")
print(f"Invoice ID: {invoice_id}")
print(f"CUFE: {uuid}")
print(f"Issue Date: {issue_date}")
print(f"Issue Time: {issue_time}")
print(f"Document Currency Code: {document_currency_code}")
print(f"Line Count: {line_count_numeric}")
print(f"--- Emisor ---")
print(f"Nombre del emisor: {supplier_name}")
print(f"ID del emisor (NIT): {supplier_id}")
print(f"Código de nivel impositivo: {supplier_tax_code}")
print(f"Dirección: {supplier_address_line}, {supplier_city}, {supplier_department}, {supplier_country}")
print(f"--- Receptor ---")
print(f"Nombre del receptor: {customer_name}")
print(f"ID del receptor (Cédula): {customer_id}")
print(f"Código de nivel impositivo: {customer_tax_code}")
print(f"Dirección: {customer_address_line}, {customer_city}, {customer_department}, {customer_country}")
print(f"--- Entrega ---")
print(f"Fecha de entrega: {delivery_date}")
print(f"Hora de entrega: {delivery_time}")
print(f"Dirección de entrega: {delivery_address_line}, {delivery_city}, {delivery_department}")
print(f"--- Información Monetaria ---")
print(f"Monto de extensión de línea: {line_extension_amount}")
print(f"Monto exclusivo de impuestos: {tax_exclusive_amount}")
print(f"Monto total con impuestos: {tax_inclusive_amount}")
print(f"Monto pagadero: {payable_amount}")
print(f"--- Línea de Factura ---")
print(f"ID de línea: {line_id}")
print(f"Cantidad facturada: {invoiced_quantity}")
print(f"Descripción del ítem: {item_description}")
print(f"Precio del ítem: {item_price}")
print(f"--- Validación DIAN ---")
print(f"Autorización DIAN: {invoice_authorization}")
print(f"Rango de facturas autorizadas: {authorized_invoices_from} - {authorized_invoices_to}")
print(f"Código de seguridad del software: {security_code}")
print(f"QR para validación DIAN: {qr_code}")





