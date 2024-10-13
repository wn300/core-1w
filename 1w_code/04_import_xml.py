
# lectura de los xlm 04_import_xml


import xml.etree.ElementTree as ET
import os
import shutil

import mysql.connector
from mysql.connector import Error


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

                idproduct = embedded_tree.find(f'.//cac:InvoiceLine[{i}]/cbc:ID', namespaces)
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
 
                    "IDline": idproduct.text if idproduct is not None else "<no disponible>",
                    "CUFE": find_cufe(root),  # Buscar CUFE con lógica condicional 
 
 
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



# Función para procesar cada archivo XML
def process_xml(xml_path, output_txt_path, cursor, connection):
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


        "ProfileID": find_element(root, './/cbc:ProfileID'),
        "UBLVersionID": find_element(root, './/cbc:UBLVersionID'),
        "IDDoc": find_element(root, './/cbc:ID'),
        "DocumentType": find_element(root, './/cbc:DocumentType'),
        "ValidationResultCode": find_element(root, './/cac:ResultOfVerification/cbc:ValidationResultCode'), 
        "ValidationDate": find_element(root, './/cac:ResultOfVerification/cbc:ValidationDate'), 
        "ValidationTime": find_element(root, './/cac:ResultOfVerification/cbc:ValidationTime'), 
        "InvoiceTypeCode": find_in_cdata(root, './/cbc:InvoiceTypeCode'), 
        "InvoiceNote": find_in_cdata(root, './/cbc:Note'),

        "DeliveryDate": find_in_cdata(root, './/cac:Delivery/cbc:ActualDeliveryDate'),  
        "DeliveryTime": find_in_cdata(root, './/cac:Delivery/cbc:ActualDeliveryTime'),  
        "DeliveryCityName": find_in_cdata(root, './/cac:Delivery/cac:DeliveryAddress/cbc:CityName'),  
        "DeliveryCountrySubentity": find_in_cdata(root, './/cac:Delivery/cac:DeliveryAddress/cbc:CountrySubentity'),  
        "DeliveryCountrySubentityCode": find_in_cdata(root, './/cac:Delivery/cac:DeliveryAddress/cbc:CountrySubentityCode'),  
        "DeliveryAddress": find_in_cdata(root, './/cac:Delivery/cac:DeliveryAddress/cac:AddressLine/cbc:Line'),  
        "DeliveryCountry": find_in_cdata(root, './/cac:Delivery/cac:DeliveryAddress/cac:Country/cbc:IdentificationCode'), 

        "PaymentID": find_in_cdata(root, './/cac:PaymentMeans/cbc:ID'), 
        "PaymentCode": find_in_cdata(root, './/cac:PaymentMeans/cbc:PaymentMeansCode'), 
        "PaymentDate": find_in_cdata(root, './/cac:PaymentMeans/cbc:PaymentDueDate'), 
        "PaymentType": find_in_cdata(root, './/cac:PaymentMeans/cbc:PaymentID'),     
        "PayableAmount": find_in_cdata(root, './/cac:LegalMonetaryTotal/cbc:PayableAmount'),


        "TaxTotal": find_in_cdata(root, './/cac:TaxTotal/cbc:TaxAmount'),     
        "TaxIND": find_in_cdata(root, './/cac:TaxTotal/cbc:TaxEvidenceIndicator'),     
        "TaxBase": find_in_cdata(root, './/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount'), 
        "TaxAmount": find_in_cdata(root, './/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount'), 
        "TaxTarifa": find_in_cdata(root, './/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent'), 
        "TaxID": find_in_cdata(root, './/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID'), 
        "TaxIDName": find_in_cdata(root, './/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name'), 

        "TotalLines": find_in_cdata(root, './/cac:LegalMonetaryTotal/cbc:LineExtensionAmount'), 
        "TotaTaxesExc": find_in_cdata(root, './/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount'),
        "TotaTaxesInc": find_in_cdata(root, './/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount'),
        "TotaDto": find_in_cdata(root, './/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount'),
        "TotaCargos": find_in_cdata(root, './/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount'),

        "InvSupplierID": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID'),#Validar la extraccion de los atributos del nit raiz
        "InvCustomerID": find_in_cdata(root, './/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID'), #Validar la extraccion de los atributos del nit raiz

        "InvSupplierNIT": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID'),
        "InvCustomerNIT": find_in_cdata(root, './/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID'), 



        "SupplierName": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name'),
        "SupplierNIT": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
        "SupplierAddress": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line'),
        "SupplierRegistrationName": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cbc:RegistrationName'),
        "SupplierTaxLevelCode": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cbc:TaxLevelCode'),
        "SupplierIDAddres": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID'),
        "SupplierCityName": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName'),
        "SupplierCountrySubentity": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity'),
        "SupplierCountrySubentityCode": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode'),
        "SupplierCountry": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode'),
        "SupplierIDTax": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID'),    
        #"SupplierIDTax": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID'),   
        "SupplierIDTaxName": find_element(root, './/cac:SenderParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name'), 
        "SupplierIndustry": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cbc:IndustryClassificationCode'), 
        "SupplierTel": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:Telephone'), 
        "SupplierMail": find_in_cdata(root, './/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail'), 


        "CustomerName": find_in_cdata(root, './/cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name'),
        "CustomerNIT": find_in_cdata(root, './/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'),
        "CustomerAddress": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CompanyID'),
        "CustomerRegistrationName": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cbc:RegistrationName'),
        "CustomerTaxLevelCode": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cbc:TaxLevelCode'),
        "CustomerIDAddres": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID'),
        "CustomerCityName": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName'),
        "CustomerCountrySubentity": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity'),
        "CustomerCountrySubentityCode": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode'),
        "CustomerCountry": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode'),
        "CustomerIDTax": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID'),    
        #"CustomerIDTax": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID'),   
        "CustomerIDTaxName": find_element(root, './/cac:ReceiverParty/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name'), 
        "CustomerTel": find_in_cdata(root, './/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:Telephone'), 
        "CustomerMail": find_in_cdata(root, './/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail'), 

    
        "LineCountNumeric": find_in_cdata(root, './/cbc:LineCountNumeric')
    }

    #print(f"Datos extraídos de {xml_path}: {VXML}")
    insert_vendor_data(cursor, VXML, connection)
    insert_comprador_data(cursor, VXML, connection)
    insert_users_data_comprador(cursor, VXML, connection)
    insert_users_data_vendedor(cursor, VXML, connection)
    insert_invoices(cursor, VXML, connection)


    # Extraer productos basados en LineCountNumeric
    line_count = int(VXML["LineCountNumeric"]) if VXML["LineCountNumeric"] != "<no disponible>" else 0
    products = extract_products(root, line_count)


    # Insertar cada línea de productos en la tabla 'invoices_lines'
    for product in products:
        insert_invoices_lines(cursor, product, connection)


    # Crear el archivo TXT con los datos extraídos
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for key, value in VXML.items():
            f.write(f"{key}: {value}\n")
        f.write("\nProductos:\n")
        for idx, product in enumerate(products, 1):
            f.write(f"Product {idx}: {product}\n")



    return VXML["CUFE"]



# Función para insertar datos en la tabla 'vendedor' con validación mejorada
def insert_vendor_data(cursor, VXML, connection):
    try:
        if not cursor or not connection.is_connected():
            print("Error: El cursor no está conectado o la conexión a la base de datos se ha perdido.")
            return

        # Obtener el NIT del vendedor
        nitvendedor = VXML.get("SupplierNIT", "<no disponible>")
        if nitvendedor in ["<no disponible>", None, ""]:
            print("Error: 'nitvendedor' no está disponible. No se puede insertar en la tabla 'vendedor'.")
            return

        # Verificar si el NIT ya existe en la tabla
        check_query = "SELECT COUNT(*) FROM vendedor WHERE nitvendedor = %s"
        cursor.execute(check_query, (nitvendedor,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Si el NIT ya existe, evitar la inserción y mostrar un mensaje
            print(f"El NIT {nitvendedor} ya existe en la tabla 'vendedor'. No se realizará la inserción.")
            return

        # Si el NIT no existe, proceder a la inserción
        query = """
            INSERT INTO vendedor (nitvendedor, razon_social, nombre_comercial, regimen_fiscal, actividad_economica, pais, departamento, municipio, direccion, telefono, mail, municipio_cod, departamento_cod, cod_tax1, ind_tax1)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            VXML.get("SupplierNIT", "<no disponible>"),
            VXML.get("SupplierName", "<no disponible>"),
            VXML.get("SupplierRegistrationName", "<no disponible>"),
            VXML.get("SupplierTaxLevelCode", "<no disponible>"),
            VXML.get("SupplierIndustry", "<no disponible>"),
            VXML.get("SupplierCountry", "<no disponible>"),
            VXML.get("SupplierCountrySubentity", "<no disponible>"),
            VXML.get("SupplierCityName", "<no disponible>"),
            VXML.get("SupplierAddress", "<no disponible>"),
            VXML.get("SupplierTel", "<no disponible>"),
            VXML.get("SupplierMail", "<no disponible>"),
            VXML.get("SupplierIDAddres", "<no disponible>"),
            VXML.get("SupplierCountrySubentityCode", "<no disponible>"),
            VXML.get("SupplierIDTax", "<no disponible>"),
            VXML.get("SupplierIDTaxName", "<no disponible>")
        )

        cursor.execute(query, values)
        connection.commit()
        print(f"Datos insertados en la tabla 'vendedor' con NIT: {nitvendedor}")

    except mysql.connector.Error as e:
        if e.errno == 1062:  # Error de clave duplicada
            print(f"Error de duplicado: El NIT {nitvendedor} ya existe en la tabla 'vendedor'.")
        else:
            print(f"Error al insertar datos en la tabla 'vendedor': {e}")
    except Error as e:
        print(f"Error al insertar datos en la tabla 'vendedor': {e}")






# Función para insertar datos en la tabla 'comprador' con validación mejorada
def insert_comprador_data(cursor, VXML, connection):
    try:
        if not cursor or not connection.is_connected():
            print("Error: El cursor no está conectado o la conexión a la base de datos se ha perdido.")
            return

        # Obtener el NIT del comprador
        nitcomprador = VXML.get("CustomerNIT", "<no disponible>")
        if nitcomprador in ["<no disponible>", None, ""]:
            print("Error: 'nitcomprador' no está disponible. No se puede insertar en la tabla 'comprador'.")
            return

        # Verificar si el NIT ya existe en la tabla
        check_query = "SELECT COUNT(*) FROM comprador WHERE nitcomprador = %s"
        cursor.execute(check_query, (nitcomprador,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Si el NIT ya existe, evitar la inserción y mostrar un mensaje
            print(f"El NIT {nitcomprador} ya existe en la tabla 'comprador'. No se realizará la inserción.")
            return

        # Si el NIT no existe, proceder a la inserción
        query = """
            INSERT INTO comprador (nitcomprador, razon_social, nombre_comercial, regimen_fiscal, pais, departamento, municipio, direccion, telefono, mail, municipio_cod, departamento_cod, cod_tax1, ind_tax1)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            VXML.get("CustomerNIT", "<no disponible>"),
            VXML.get("CustomerName", "<no disponible>"),
            VXML.get("CustomerRegistrationName", "<no disponible>"),
            VXML.get("CustomerTaxLevelCode", "<no disponible>"),
            VXML.get("CustomerCountry", "<no disponible>"),
            VXML.get("CustomerCountrySubentity", "<no disponible>"),
            VXML.get("CustomerCityName", "<no disponible>"),
            VXML.get("CustomerAddress", "<no disponible>"),
            VXML.get("CustomerTel", "<no disponible>"),
            VXML.get("CustomerMail", "<no disponible>"),
            VXML.get("CustomerIDAddres", "<no disponible>"),
            VXML.get("CustomerCountrySubentityCode", "<no disponible>"),
            VXML.get("CustomerIDTax", "<no disponible>"),
            VXML.get("CustomerIDTaxName", "<no disponible>")
        )

        cursor.execute(query, values)
        connection.commit()
        print(f"Datos insertados en la tabla 'comprador' con NIT: {nitcomprador}")

    except mysql.connector.Error as e:
        if e.errno == 1062:  # Error de clave duplicada
            print(f"Error de duplicado: El NIT {nitcomprador} ya existe en la tabla 'comprador'.")
        else:
            print(f"Error al insertar datos en la tabla 'comprador': {e}")
    except Error as e:
        print(f"Error al insertar datos en la tabla 'comprador': {e}")





# Función para insertar datos en la tabla 'users' con validación mejorada
def insert_users_data_comprador(cursor, VXML, connection):
    try:
        if not cursor or not connection.is_connected():
            print("Error: El cursor no está conectado o la conexión a la base de datos se ha perdido.")
            return

        # Obtener el ID del user
        id_user = VXML.get("CustomerNIT", "<no disponible>")
        if id_user in ["<no disponible>", None, ""]:
            print("Error: 'nitcomprador' no está disponible. No se puede insertar en la tabla 'users'.")
            return

        # Verificar si el users ya existe en la tabla
        check_query = "SELECT COUNT(*) FROM users WHERE id_user = %s"
        cursor.execute(check_query, (id_user,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Si el id_user ya existe, evitar la inserción y mostrar un mensaje
            print(f"El user {id_user} ya existe en la tabla 'users'. No se realizará la inserción.")
            return

        # Si el id_user no existe, proceder a la inserción
        query = """
            INSERT INTO users (id_user, name_user,mail)
            VALUES (%s, %s, %s)
        """
        values = (
            VXML.get("CustomerNIT", "<no disponible>"),
            VXML.get("CustomerRegistrationName", "<no disponible>"),
            VXML.get("CustomerMail", "<no disponible>"),            
        )

        cursor.execute(query, values)
        connection.commit()
        print(f"Datos insertados en la tabla 'users' con id_user: {id_user}")

    except mysql.connector.Error as e:
        if e.errno == 1062:  # Error de clave duplicada
            print(f"Error de duplicado: El User {id_user} ya existe en la tabla 'users'.")
        else:
            print(f"Error al insertar datos en la tabla 'users': {e}")
    except Error as e:
        print(f"Error al insertar datos en la tabla 'users': {e}")






# Función para insertar datos en la tabla 'users' con validación mejorada
def insert_users_data_vendedor(cursor, VXML, connection):
    try:
        if not cursor or not connection.is_connected():
            print("Error: El cursor no está conectado o la conexión a la base de datos se ha perdido.")
            return

        # Obtener el ID del user
        id_user = VXML.get("SupplierNIT", "<no disponible>")
        if id_user in ["<no disponible>", None, ""]:
            print("Error: 'nitvendedor' no está disponible. No se puede insertar en la tabla 'users'.")
            return

        # Verificar si el users ya existe en la tabla
        check_query = "SELECT COUNT(*) FROM users WHERE id_user = %s"
        cursor.execute(check_query, (id_user,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Si el id_user ya existe, evitar la inserción y mostrar un mensaje
            print(f"El user {id_user} ya existe en la tabla 'users'. No se realizará la inserción.")
            return

        # Si el id_user no existe, proceder a la inserción
        query = """
            INSERT INTO users (id_user, name_user,mail)
            VALUES (%s, %s, %s)
        """
        values = (
            VXML.get("SupplierNIT", "<no disponible>"),
            VXML.get("SupplierRegistrationName", "<no disponible>"),
            VXML.get("SupplierMail", "<no disponible>"),            
        )

        cursor.execute(query, values)
        connection.commit()
        print(f"Datos insertados en la tabla 'users' con id_user: {id_user}")

    except mysql.connector.Error as e:
        if e.errno == 1062:  # Error de clave duplicada
            print(f"Error de duplicado: El User {id_user} ya existe en la tabla 'users'.")
        else:
            print(f"Error al insertar datos en la tabla 'users': {e}")
    except Error as e:
        print(f"Error al insertar datos en la tabla 'users': {e}")



# Función para insertar datos en la tabla 'invoices' con validación mejorada
def insert_invoices(cursor, VXML, connection):
    try:
        if not cursor or not connection.is_connected():
            print("Error: El cursor no está conectado o la conexión a la base de datos se ha perdido.")
            return

        # Obtener el cufe del documento
        cufe = VXML.get("CUFE", "<no disponible>")
        if cufe in ["<no disponible>", None, ""]:
            print("Error: 'CUFE' no está disponible. No se puede insertar en la tabla 'invoices'.")
            return

        # Verificar si el CUFE ya existe en la tabla
        check_query = "SELECT COUNT(*) FROM invoices WHERE cufe = %s"
        cursor.execute(check_query, (cufe,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Si el CUFE ya existe, evitar la inserción y mostrar un mensaje
            print(f"El CUFE {cufe} ya existe en la tabla 'invoices'. No se realizará la inserción.")
            return

        # Si el CUFE no existe, proceder a la inserción
        query = """
            INSERT INTO invoices (cufe, no_fact, fecha_emision, hora_emision, fecha_vencimiento, moneda_doc, version, version_ubl, legal_iddoc, tipo_doc, validacion_cod, fecha_validacion, hora_validacion, tipo_doc_cod, nota, fecha_envio, hora_envio, ciudad_envio, departamento_envio, departamento_cod, direccion_envio, pais_emision, pago_id, pago_code, fecha_pago, pago_tipo, valor_pago, valor_impuestos_total, ind_tax_factura, valor_base_impuestos, valor_impuestos, tarifa_impuestos, id_tax_factura, nombre_tax_factura, valor_total_factura, valor_impuestos_exc, valor_impuestos_inc, valor_descuentos, valor_cargos, nro_items_doc, vendedor_id, comprador_id, nitvendedor, nitcomprador)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            VXML.get("CUFE", "<no disponible>"),
            VXML.get("InvoiceID", "<no disponible>"),
            VXML.get("IssueDate", "<no disponible>"),
            VXML.get("IssueTime", "<no disponible>"),
            VXML.get("DueDate") if VXML.get("DueDate") != "<no disponible>" else None,
            VXML.get("DocumentCurrencyCode", "<no disponible>"),
            VXML.get("ProfileID", "<no disponible>"),
            VXML.get("UBLVersionID", "<no disponible>"),
            VXML.get("IDDoc", "<no disponible>"),
            VXML.get("DocumentType", "<no disponible>"),
            VXML.get("ValidationResultCode", "<no disponible>"),
            VXML.get("ValidationDate", None),
            VXML.get("ValidationTime", "<no disponible>"),
            VXML.get("InvoiceTypeCode", "<no disponible>"),
            VXML.get("InvoiceNote", "<no disponible>"),
            VXML.get("DeliveryDate") if VXML.get("DeliveryDate") != "<no disponible>" else None,
            VXML.get("DeliveryTime", "<no disponible>") ,
            VXML.get("DeliveryCityName", "<no disponible>"),
            VXML.get("DeliveryCountrySubentity", "<no disponible>"),
            VXML.get("DeliveryCountrySubentityCode", "<no disponible>"),
            VXML.get("DeliveryAddress", "<no disponible>"),
            VXML.get("DeliveryCountry", "<no disponible>"),
            VXML.get("PaymentID", "<no disponible>"),
            VXML.get("PaymentCode", "<no disponible>"),
            VXML.get("PaymentDate") if VXML.get("PaymentDate") != "<no disponible>" else None,
            VXML.get("PaymentType", "<no disponible>"),
            VXML.get("PayableAmount", "<no disponible>"),
            VXML.get("TaxTotal") if VXML.get("TaxTotal") != "<no disponible>" else None,
            VXML.get("TaxIND", "<no disponible>"),
            VXML.get("TaxBase") if VXML.get("TaxBase") != "<no disponible>" else None,
            VXML.get("TaxAmount") if VXML.get("TaxAmount") != "<no disponible>" else None,
            VXML.get("TaxTarifa") if VXML.get("TaxTarifa") != "<no disponible>" else None,
            VXML.get("TaxID", "<no disponible>"),
            VXML.get("TaxIDName", "<no disponible>"),
            VXML.get("TotalLines", "<no disponible>"),
            VXML.get("TotaTaxesExc", "<no disponible>"),
            VXML.get("TotaTaxesInc", "<no disponible>"),
            VXML.get("TotaDto") if VXML.get("TotaDto") != "<no disponible>" else None,
            VXML.get("TotaCargos") if VXML.get("TotaCargos") != "<no disponible>" else None,
            VXML.get("LineCountNumeric", "<no disponible>"),
            VXML.get("InvSupplierID", "<no disponible>"),
            VXML.get("InvCustomerID") if VXML.get("InvCustomerID") != "<no disponible>" else VXML.get("CustomerNIT", None),
            VXML.get("InvSupplierNIT", "<no disponible>"),
            VXML.get("InvCustomerNIT") if VXML.get("InvCustomerNIT") != "<no disponible>" else VXML.get("CustomerNIT", None),
        )

        cursor.execute(query, values)
        connection.commit()
        print(f"Datos insertados en la tabla 'invoices' con CUFE: {cufe}")

    except mysql.connector.Error as e:
        if e.errno == 1062:  # Error de clave duplicada
            print(f"Error de duplicado: El CUFE {cufe} ya existe en la tabla 'invoices'.")
        else:
            print(f"Error al insertar datos en la tabla 'invoices': {e}")
    except Error as e:
        print(f"Error al insertar datos en la tabla 'invoices': {e}")




# Función para insertar datos en la tabla 'invoices_lines' con validación de duplicados
def insert_invoices_lines(cursor, product_data, connection):
    try:
        if not cursor or not connection.is_connected():
            print("Error: El cursor no está conectado o la conexión a la base de datos se ha perdido.")
            return

        # Obtener los valores de IDline y CUFE
        idline = product_data.get("IDline", "<no disponible>")
        cufe = product_data.get("CUFE", "<no disponible>")

        # Verificar si la combinación de IDline y CUFE ya existe en la tabla
        check_query = "SELECT COUNT(*) FROM invoices_lines WHERE idline = %s AND cufe = %s"
        cursor.execute(check_query, (idline, cufe))
        count = cursor.fetchone()[0]

        if count > 0:
            # Si la combinación ya existe, evitar la inserción y mostrar un mensaje
            print(f"El id {idline} y CUFE {cufe} ya existe en la tabla 'invoices_lines'. No se realizará la inserción.")
            return

        # Si la combinación no existe, proceder a la inserción
        insert_query = """
            INSERT INTO invoices_lines (idline, cufe, codigo, descripcion, cantidad, precio_un, tax_line, porcentaje_tax_line, total_line, total_tax_line, total_basetax_line, id_tax_line, id_nametax_line, codigost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            product_data.get("IDline", "<no disponible>"),
            product_data.get("CUFE", "<no disponible>"),
            product_data.get("ITID", "<no disponible>"),
            product_data.get("ITDes", "<no disponible>"),
            product_data.get("ITQ", 0),
            product_data.get("ITP", 0),
            product_data.get("ITTaxVr", 0),
            product_data.get("ITTaxPr", 0),
            product_data.get("ITVr", 0),
            product_data.get("ITTax", 0),
            product_data.get("ITTaxBase", 0),
            product_data.get("ITTaxID", "<no disponible>"),
            product_data.get("ITTaxName", "<no disponible>"),
            product_data.get("ITST", "<no disponible>")
        )

        cursor.execute(insert_query, values)
        connection.commit()
        print(f"Línea con id {idline} y CUFE {cufe} insertada correctamente en la tabla 'invoices_lines'.")

    except mysql.connector.Error as e:
        print(f"Error al insertar datos en la tabla 'invoices_lines': {e}")
    except Error as e:
        print(f"Error al insertar datos en la tabla 'invoices_lines': {e}")



# Función para procesar las carpetas
def process_folders(base_path):
    
    
    connection = None
    cursor = None    
    
       
    
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Matkus2107",
            database="1w"
        )
        if connection.is_connected():
            print("Conexión exitosa a MySQL")
            cursor = connection.cursor()

            folders = [f.path for f in os.scandir(base_path) if f.is_dir()]
            print(f"Encontradas {len(folders)} carpetas.")

            for folder in folders:
                xml_files = [f for f in os.listdir(folder) if f.endswith('.xml')]
                if not xml_files:
                    print(f"No se encontró ningún archivo XML en {folder}")
                    continue

                xml_path = os.path.join(folder, xml_files[0])
                output_txt_path = os.path.join(folder, 'VXML_data.txt')

                # Procesar el archivo XML y obtener el CUFE, pasando la conexión
                cufe = process_xml(xml_path, output_txt_path, cursor, connection)
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

            # Confirmar la transacción y cerrar la conexión
            connection.commit()
            print("Transacción confirmada en MySQL")

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    finally:
        # Cerrar conexión y cursor aquí solo después de todos los procesos
        if cursor is not None:
            cursor.close()
            print("Cursor cerrado correctamente.")
        if connection is not None and connection.is_connected():
            connection.close()
            print("Conexión a MySQL cerrada.")
    
    
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
        cufe = process_xml(xml_path, output_txt_path, cursor, connection)
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