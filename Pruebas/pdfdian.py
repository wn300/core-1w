import PyPDF2
import re

# Ruta del archivo PDF en el proyecto PDFDIAN
pdf_path = r"c:\temp\DIAN_0820028cee297b2fc8932277fa23942720bd6331e34c5ecdb89f557fbefa88872411764463ab774c1f4e2c13682f2b93.pdf"

def imprimir_pdf_con_varok(pdf_file_path):
        # Abre el archivo PDF
        with open(pdf_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extrae el texto de la primera página
            if len(pdf_reader.pages) > 0:
                page = pdf_reader.pages[0]
                text = page.extract_text() or ""  # Asegura que no sea None

                # Imprime el contenido de la primera página del PDF
                print("Contenido de la primera página del PDF:")
                print(text)
                print("\n=================\n")

        # Expresiones regulares para las variables en varok
        patterns = {
            "CUFE": r":\s*(\S+)",
            "Número de Factura": r"Número de Factura:\s*(\S+)",
            "Fecha de Emisión": r"Fecha de Emisión:\s*(\d{2}/\d{2}/\d{4})",
            "Fecha de Vencimiento": r"Fecha de Vencimiento:\s*(\d{2}/\d{2}/\d{4})",
            "Tipo de Operación": r"Tipo de Operación:\s*(.*)",
            "Forma de Pago": r"Forma de pago:\s*(.*)",
            "Medio de Pago": r"Medio de Pago:\s*(.*)",
            "Orden de Pedido": r"Orden de pedido:\s*(.*)",
            "Fecha de Orden de Pedido": r"Fecha de orden de pedido:\s*(.*)",
            "Razón Social": r"Razón Social:\s*(.*)",
            "Nombre Comercial": r"Nombre Comercial:\s*(.*)",
            "NIT del Emisor": r"Nit del Emisor:\s*(.*)",
            "Tipo de Contribuyente": r"Tipo de Contribuyente:\s*(.*)",
            "Dirección del Emisor": r"Dirección:\s*(.*)",
            "Teléfono del Emisor": r"Teléfono / Móvil:\s*(.*)",
            "Correo del Emisor": r"Correo:\s*(.*)",
            "País del Emisor": r"País:\s*(.*)",
            "Departamento del Emisor": r"Departamento:\s*(.*)",
            "Municipio del Emisor": r"Municipio / Ciudad:\s*(.*)",
            "Régimen Fiscal": r"Régimen Fiscal:\s*(.*)",
            "Responsabilidad Tributaria": r"Responsabilidad Tributaria:\s*(.*)",
            "Actividad Económica": r"Actividad Económica:\s*(.*)",
            "Nombre Comprador": r"Nombre o Razón Social:\s*(.*)",
            "Tipo Documento Comprador": r"Tipo de Documento:\s*(.*)",
            "Número Documento Comprador": r"Número Documento:\s*(.*)",
            "Tipo Contribuyente Comprador": r"Tipo de Contribuyente:\s*(.*)",
            "País Comprador": r"País:\s*(.*)",
            "Departamento Comprador": r"Departamento:\s*(.*)",
            "Municipio Comprador": r"Municipio / Ciudad:\s*(.*)",
            "Régimen Fiscal Comprador": r"Régimen fiscal:\s*(.*)",
            "Responsabilidad Tributaria Comprador": r"Responsabilidad tributaria:\s*(.*)",
            "Dirección Comprador": r"Dirección:\s*(.*)",
            "Teléfono Comprador": r"Teléfono / Móvil:\s*(.*)",
            "Correo Comprador": r"Correo:\s*(.*)",
            "Moneda": r"Moneda:\s*(.*)",
            "Tasa de Cambio": r"Tasa de Cambio:\s*(.*)",
            "Subtotal": r"Subtotal:\s*(.*)",
            "Descuento Detalle": r"Descuento Detalle:\s*(.*)",
            "Recargo Detalle": r"Recargo Detalle:\s*(.*)",
            "Total Bruto Factura": r"Total Bruto Factura:\s*(.*)",
            "IVA": r"IVA:\s*(.*)",
            "INC": r"INC:\s*(.*)",
            "Bolsas": r"Bolsas:\s*(.*)",
            "Otros Impuestos": r"Otros Impuestos:\s*(.*)",
            "Total Impuesto": r"Total Impuesto:\s*(.*)",
            "Total Neto Factura": r"Total Neto Factura:\s*(.*)",
            "Descuento Global": r"Descuento Global:\s*(.*)",
            "Recargo Global": r"Recargo Global:\s*(.*)",
            "Total Factura": r"Total Factura:\s*(.*)",
            "Anticipos": r"Anticipos:\s*(.*)",
            "Rete Fuente": r"Rete Fuente:\s*(.*)",
            "Rete IVA": r"Rete IVA:\s*(.*)",
            "Rete ICA": r"Rete ICA:\s*(.*)",
        }

        # Extraer y mostrar las variables validadas en varok
        print("Variables extraídas (varok):")
        for variable, pattern in patterns.items():
            match = re.search(pattern, text)
            print(f"{variable}: {match.group(1) if match else '<no disponible>'}")

# Ejecutar la función para imprimir el PDF y las variables validadas en varok
imprimir_pdf_con_varok(pdf_path)

















