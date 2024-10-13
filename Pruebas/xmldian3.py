from lxml import etree

# Ajustar el diccionario VXML con las rutas basadas en la estructura proporcionada
VXML = {
    "UBLVersionID": "cbc:UBLVersionID",
    "CustomizationID": "cbc:CustomizationID",
    "ProfileID": "cbc:ProfileID",
    "ProfileExecutionID": "cbc:ProfileExecutionID",
    "DocumentID": "cbc:ID",
    "UUID": "cbc:UUID",
    "IssueDate": "cbc:IssueDate",
    "IssueTime": "cbc:IssueTime",
    "DocumentType": "cbc:DocumentType",
    "ParentDocumentID": "cbc:ParentDocumentID",
    "DocumentCurrencyCode": "cbc:DocumentCurrencyCode",
    "LineCountNumeric": "cbc:LineCountNumeric",
    
    # Emisor (SenderParty)
    "SupplierName": "cac:SenderParty/cac:PartyTaxScheme/cbc:RegistrationName",
    "SupplierTaxID": "cac:SenderParty/cac:PartyTaxScheme/cbc:CompanyID",
    "SupplierCityName": "cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName",
    "SupplierCountrySubentity": "cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity",
    "SupplierCountrySubentityCode": "cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode",
    "SupplierAddressLine": "cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line",
    
    # Receptor (ReceiverParty)
    "CustomerName": "cac:ReceiverParty/cac:PartyTaxScheme/cbc:RegistrationName",
    "CustomerTaxID": "cac:ReceiverParty/cac:PartyTaxScheme/cbc:CompanyID",
    "CustomerCityName": "cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName",
    "CustomerCountrySubentity": "cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity",
    "CustomerCountrySubentityCode": "cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode",
    "CustomerAddressLine": "cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line",
    
    # Información de Factura
    "InvoiceReferenceID": "cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID",
    "InvoiceReferenceUUID": "cac:BillingReference/cac:InvoiceDocumentReference/cbc:UUID",
    "InvoiceReferenceIssueDate": "cac:BillingReference/cac:InvoiceDocumentReference/cbc:IssueDate",
    "InvoiceReferenceDocumentTypeCode": "cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode",
    
    # Información Monetaria
    "TaxAmount": "cac:TaxTotal/cbc:TaxAmount",
    "TaxableAmount": "cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount",
    "LegalMonetaryLineExtensionAmount": "cac:LegalMonetaryTotal/cbc:LineExtensionAmount",
    "LegalMonetaryTaxExclusiveAmount": "cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount",
    "LegalMonetaryTaxInclusiveAmount": "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount",
    "LegalMonetaryAllowanceTotalAmount": "cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount",
    "LegalMonetaryChargeTotalAmount": "cac:LegalMonetaryTotal/cbc:ChargeTotalAmount",
    "LegalMonetaryPayableAmount": "cac:LegalMonetaryTotal/cbc:PayableAmount",
    
    # Detalles de Producto (CreditNoteLine) con manejo específico para elementos anidados
    "ItemDescription": "cac:CreditNoteLine/cac:Item/cbc:Description",
    "CreditedQuantity": "cac:CreditNoteLine/cbc:CreditedQuantity",
    "LineExtensionAmount": "cac:CreditNoteLine/cbc:LineExtensionAmount",
    "PriceAmount": "cac:CreditNoteLine/cac:Price/cbc:PriceAmount",
    # Ajuste para elementos de lotes de productos
    "ItemLotNumberID": "cac:CreditNoteLine/cac:Item/cac:ItemInstance/cac:LotIdentification/cbc:LotNumberID",
    "ItemExpiryDate": "cac:CreditNoteLine/cac:Item/cac:ItemInstance/cac:LotIdentification/cbc:ExpiryDate",
    
    # Información Adicional
    "TaxRepresentativePartyID": "cac:TaxRepresentativeParty/cac:PartyIdentification/cbc:ID",
    "TaxRepresentativePartyName": "cac:TaxRepresentativeParty/cac:PartyName/cbc:Name",
    "DeliveryDate": "cac:Delivery/cbc:ActualDeliveryDate",
    "DeliveryTime": "cac:Delivery/cbc:ActualDeliveryTime",
    "DeliveryCityName": "cac:Delivery/cac:DeliveryAddress/cbc:CityName",
    "DeliveryAddressLine": "cac:Delivery/cac:DeliveryAddress/cac:AddressLine/cbc:Line",
    
    # Información de control de la DIAN y otros
    "DIANAuthorization": "cac:Attachment/cac:ExternalReference/cbc:Description",
    "AuthorizationStartDate": "cac:Attachment/cac:ExternalReference/cbc:Description",
    "AuthorizationEndDate": "cac:Attachment/cac:ExternalReference/cbc:Description",
    "QRCode": "cac:Attachment/cac:ExternalReference/cbc:Description",
}

# Ruta al archivo XML proporcionado
xml_file_path = r'c:\1wdoc\ad09005910380002400059222.xml'

# Función para recorrer y obtener los valores
def parse_xml_and_extract_values(xml_file, dictionary):
    tree = etree.parse(xml_file)
    root = tree.getroot()
    ns = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'sts': 'dian:gov:co:facturaelectronica:Structures-2-1'
    }
    
    results = {}
    for key, path in dictionary.items():
        # Buscar el elemento utilizando la ruta y el namespace
        element = root.xpath(path, namespaces=ns)
        
        # Extraer texto si se encuentra el elemento
        # Manejar casos donde hay múltiples elementos
        if element:
            if isinstance(element, list) and len(element) > 0:
                # Unir los textos si hay múltiples resultados
                results[key] = " | ".join([el.text for el in element if el is not None and el.text])
            else:
                results[key] = element[0].text if element[0].text is not None else "<nodisponibles>"
        else:
            results[key] = "<nodisponibles>"
    
    # Contar los nodos en el XML
    total_nodes = len(list(root.iter()))
    return results, total_nodes

# Ejecutar la función y obtener los valores
values, node_count = parse_xml_and_extract_values(xml_file_path, VXML)

# Imprimir resultados en el formato de "variable = valor"
print("\nValores extraídos:")
for key, value in values.items():
    print(f"{key} = {value}")
print(f"\nTotal de nodos en el XML: {node_count}")






