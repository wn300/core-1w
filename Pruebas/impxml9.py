import xml.etree.ElementTree as ET
import os

# Ruta del archivo XML
xml_path = r'C:\1wdoc\ad09005910380002400159803.xml'
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

# Función para extraer productos
def extract_products(line_count):
    description_element = root.find('.//cbc:Description', namespaces)
    products = []
    if description_element is not None and description_element.text:
        try:
            # Parsear el contenido del CDATA como un nuevo XML
            embedded_tree = ET.fromstring(description_element.text)
            for i in range(1, line_count + 1):
                product_description = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:Item/cbc:Description', namespaces)
                product_quantity = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cbc:InvoicedQuantity', namespaces)
                product_price = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:Price/cbc:PriceAmount', namespaces)

                product_TaxAmount = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:TaxTotal/cbc:TaxAmount', namespaces)
                product_TaxableAmount = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount', namespaces)
                product_TaxAmount = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount', namespaces)

                product_TaxPercent = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent', namespaces)
                product_TaxID = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID', namespaces)
                product_TaxName = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name', namespaces)

                product_line_extension = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cbc:LineExtensionAmount', namespaces)
                SellersItemIdentification = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:Item/cac:SellersItemIdentification/cbc:ID', namespaces)
                StandardItemIdentification = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cac:Item/cac:StandardItemIdentification/cbc:ID', namespaces)                
                product_data = {
                    "ITDes": product_description.text if product_description is not None else "<no disponible>",
                    "ITQ": product_quantity.text if product_quantity is not None else "<no disponible>",
                    "ITP": product_price.text if product_price is not None else "<no disponible>",   

                    "ITTax": product_TaxAmount.text if product_TaxAmount is not None else "<no disponible>",  
                    "ITTaxBase": product_TaxableAmount.text if product_TaxableAmount is not None else "<no disponible>", 
                    "ITTaxVr": product_TaxAmount.text if product_TaxAmount is not None else "<no disponible>", 

                    "ITTaxPr": product_TaxPercent.text if product_TaxPercent is not None else "<no disponible>", 
                    "ITTaxID": product_TaxID.text if product_TaxID is not None else "<no disponible>", 
                    "ITTaxName": product_TaxName.text if product_TaxName is not None else "<no disponible>", 

                    "ITVr": product_line_extension.text if product_line_extension is not None else "<no disponible>",
                    "ITID": SellersItemIdentification.text if SellersItemIdentification is not None else "<no disponible>",
                    "ITST": StandardItemIdentification.text if StandardItemIdentification is not None else "<no disponible>",                                      
                }
                products.append(product_data)
        except ET.ParseError:
            return "<error en el CDATA>"
    return products

# Extraer los 17 campos, incluyendo LineCountNumeric
VXML = {
    "CUFE": find_element('.//cbc:UUID'),
    "InvoiceID": find_element('.//cbc:ParentDocumentID'),
    "IssueDate": find_in_cdata('.//cbc:IssueDate'),
    "IssueTime": find_in_cdata('.//cbc:IssueTime'),
    "DueDate": find_in_cdata('.//cbc:DueDate'), 

    "ProfileID": find_element('.//cbc:ProfileID'),
    "UBLVersionID": find_element('.//cbc:UBLVersionID'),
    "IDDoc": find_element('.//cbc:ID'),
    "DocumentType": find_element('.//cbc:DocumentType'),
    "ValidationResultCode": find_element('.//cac:ResultOfVerification/cbc:ValidationResultCode'), 
    "ValidationDate": find_element('.//cac:ResultOfVerification/cbc:ValidationDate'), 
    "ValidationTime": find_element('.//cac:ResultOfVerification/cbc:ValidationTime'), 
    "InvoiceTypeCode": find_in_cdata('.//cbc:InvoiceTypeCode'), 
    "InvoiceNote": find_in_cdata('.//cbc:Note'), 

    "DeliveryDate": find_in_cdata('.//cac:Delivery/cbc:ActualDeliveryDate'),  
    "DeliveryTime": find_in_cdata('.//cac:Delivery/cbc:ActualDeliveryTime'),  
    "DeliveryCityName": find_in_cdata('.//cac:Delivery/cac:DeliveryAddress/cbc:CityName'),  
    "DeliveryCountrySubentity": find_in_cdata('.//cac:Delivery/cac:DeliveryAddress/cbc:CountrySubentity'),  
    "DeliveryCountrySubentityCode": find_in_cdata('.//cac:Delivery/cac:DeliveryAddress/cbc:CountrySubentityCode'),  
    "DeliveryAddress": find_in_cdata('.//cac:Delivery/cac:DeliveryAddress/cac:AddressLine/cbc:Line'),  
    "DeliveryCountry": find_in_cdata('.//cac:Delivery/cac:DeliveryAddress/cac:Country/cbc:IdentificationCode'), 

    "PaymentID": find_in_cdata('.//cac:PaymentMeans/cbc:ID'), 
    "PaymentCode": find_in_cdata('.//cac:PaymentMeans/cbc:PaymentMeansCode'), 
    "PaymentDate": find_in_cdata('.//cac:PaymentMeans/cbc:PaymentDueDate'), 
    "PaymentType": find_in_cdata('.//cac:PaymentMeans/cbc:PaymentID'),     

    "TaxTotal": find_in_cdata('.//cac:TaxTotal/cbc:TaxAmount'),     
    "TaxIND": find_in_cdata('.//cac:TaxTotal/cbc:TaxEvidenceIndicator'),     
    "TaxBase": find_in_cdata('.//cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount'), 
    "TaxAmount": find_in_cdata('.//cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount'), 
    "TaxTarifa": find_in_cdata('.//cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent'), 
    "TaxID": find_in_cdata('.//cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID'), 
    "TaxIDName": find_in_cdata('.//cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name'), 

   "TotalLines": find_in_cdata('.//cac:LegalMonetaryTotal/cbc:LineExtensionAmount'), 
   "TotaTaxesExc": find_in_cdata('.//cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount'),
   "TotaTaxesInc": find_in_cdata('.//cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount'),
   "TotaDto": find_in_cdata('.//cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount'),
   "TotaCargos": find_in_cdata('.//cac:LegalMonetaryTotal/cbc:ChargeTotalAmount'),

    "SupplierRegistrationName": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cbc:RegistrationName'),
    "SupplierTaxLevelCode": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cbc:TaxLevelCode'),
    "SupplierIDAddres": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID'),
    "SupplierCityName": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName'),
    "SupplierCountrySubentity": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity'),
    "SupplierCountrySubentityCode": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode'),
    "SupplierCountry": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode'),
    "SupplierIDTax": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID'),    
    #"SupplierIDTax": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID'),   
    "SupplierIDTaxName": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name'), 
    "SupplierIndustry": find_in_cdata('.//cac:AccountingSupplierParty/cac:Party/cbc:IndustryClassificationCode'), 
    "SupplierTel": find_in_cdata('.//cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telephone'), 
    "SupplierMail": find_in_cdata('.//cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail'), 

    "CustomerRegistrationName": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cbc:RegistrationName'),
    "CustomerTaxLevelCode": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cbc:TaxLevelCode'),
    "CustomerIDAddres": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID'),
    "CustomerCityName": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName'),
    "CustomerCountrySubentity": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity'),
    "CustomerCountrySubentityCode": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode'),
    "CustomerCountry": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode'),
    "CustomerIDTax": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID'),    
    #"CustomerIDTax": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID'),   
    "CustomerIDTaxName": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name'), 
    "CustomerTel": find_in_cdata('.//cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:Telephone'), 
    "CustomerMail": find_in_cdata('.//cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail'), 

    "DocumentCurrencyCode": find_in_cdata('.//cbc:DocumentCurrencyCode'),  
    "SupplierName": find_in_cdata('.//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name'),
    "SupplierNIT": find_in_cdata('.//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
    "SupplierAddress": find_element('.//cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line'),
    "CustomerName": find_in_cdata('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name'),
    "CustomerID": find_in_cdata('.//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
    "CustomerAddress": find_element('.//cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line'),
    "PayableAmount": find_in_cdata('.//cac:LegalMonetaryTotal/cbc:PayableAmount'),
    "LineCountNumeric": find_in_cdata('.//cbc:LineCountNumeric')
}

# Extraer productos basados en LineCountNumeric
line_count = int(VXML["LineCountNumeric"]) if VXML["LineCountNumeric"] != "<no disponible>" else 0
products = extract_products(line_count)

# Imprimir el resultado
for key, value in VXML.items():
    print(f"{key}: {value}")

# Imprimir los productos
for idx, product in enumerate(products, 1):
    print(f"Product {idx}: {product}")

# Crear el directorio si no existe
os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)

# Guardar los datos en un archivo txt
with open(output_txt_path, 'w', encoding='utf-8') as f:
    for key, value in VXML.items():
        f.write(f"{key}: {value}\n")
    f.write("\nProductos:\n")
    for idx, product in enumerate(products, 1):
        f.write(f"Product {idx}: {product}\n")

print(f"Datos guardados en {output_txt_path}")
