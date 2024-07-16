import json
import requests
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

from reportlab.lib.units import inch
import textwrap
from reportlab.lib.colors import black



def load_json_file(file_path):
    encodings = ['utf-8-sig', 'utf-8', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return json.load(file)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo decodificar el archivo con ninguna de las codificaciones: {encodings}")

try:
    data = load_json_file('C:/Users/andy_/Downloads/test.json')
except ValueError as e:
    print(f"Error al cargar el archivo: {e}")
    exit(1)


categories = {
    "Camiseta Oversize": ["Camiseta"],
    "Jogger": ["Jogger"],
    "Hoodie Oversize": ["Hoodie", "Oversize Fit"],
    "Hoodie Oversize con Cierre": ["Hoodie Oversize", "con Cierre"],
    "Pantaloneta": ["Pantaloneta"],
    "Hoodie Relaxed Fit": ["Hoodie", "Relaxed"]
}

def categorize_product(name):
    name_lower = name.lower()
    for category, keywords in categories.items():
        if all(keyword.lower() in name_lower for keyword in keywords):
            return category
    return "Sin categoría"

# Clasificar productos
classified_products = {}
for product in data:
    if product['Stock'] != "" and product['Stock'] != "0":
        category = categorize_product(product['Name'])
        talla = product['Attribute Pa Talla']
        if category not in classified_products:
            classified_products[category] = {}
        if talla not in classified_products[category]:
            classified_products[category][talla] = []
        classified_products[category][talla].append(product)



# Función para descargar una imagen
def download_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))




# Función para crear un PDF con las imágenes
def create_pdf(products, category, size):
    pdf_filename = f"{category}_{size}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    # Ajustar el espacio entre filas e imágenes
    space_between_rows = 3.5 * inch  # Espacio entre filas de imágenes
    space_between_columns = 4 * inch  # Espacio entre columnas de imágenes

    def add_product_to_page(product, x, y):
        # Descargar y redimensionar la imagen
        image_url = product['Thumbnail Id']
        try:
            img = download_image(image_url)
            img_width, img_height = img.size
            aspect = img_height / float(img_width)
            
            display_width = 2.0 * inch
            display_height = display_width * aspect

            # Guardar la imagen como PNG temporal
            temp_filename = f"temp_image_{product['SKU']}.png"
            img.save(temp_filename, "PNG")

            # Dibujar sombra
            c.setFillColor(black)
            c.rect(x - 3, y - display_height - 5, display_width, display_height, fill=1)

            # Añadir la imagen al PDF
            #CAMBIOSSSSSSSSSSSS -4
            c.drawImage(temp_filename, x + 2, y - display_height, width=display_width, height=display_height)
            
            # Dibujar contorno negro
            c.setStrokeColor(black)
            c.rect(x + 2, y - display_height, display_width, display_height, fill=0)

            # Añadir información del producto
            c.setFont("Helvetica", 12)
            
            # Extraer el nombre del producto hasta el símbolo '-'
            product_name = product['Name'].split('-')[0].strip()
            
            wrapped_lines = textwrap.wrap(product_name, width=15)  # Dividir en líneas de hasta 15 caracteres
            text_y = y - 50
            for line in wrapped_lines:
                c.drawString(x + 2.35 * inch, text_y, line)
                text_y -= 14  # Espaciado entre líneas

            c.drawString(x + 2.35 * inch, y - 99, f"Color {product['Attribute Pa Color']}")
            
            c.setFont("Helvetica-Bold", 15)  # Fuente en negrita para parte del texto
            c.drawString(x + 2.35 * inch, y - 120, f"{product['Attribute Pa Talla']}")
            
            c.setFont("Helvetica", 12)  # Fuente normal para 'Disponible'
            c.drawString(x + 2.35 * inch, y - 154, f"${product['Regular Price']}")
            c.drawString(x + 2.35 * inch, y - 168, f"Disponible: {product['Stock']}")

            # Eliminar el archivo temporal
            os.remove(temp_filename)

        except Exception as e:
            print(f"Error al procesar la imagen de {product['Name']}: {e}")

    for i, product in enumerate(products):
        page_position = i % 6
        if page_position == 0 and i != 0:
            c.showPage()  # Nueva página

        row = page_position // 2
        col = page_position % 2

        # Ajustar las coordenadas x e y para cada imagen
        x = 0.5 * inch + col * space_between_columns
        y = height - (0.5 * inch + row * space_between_rows)

        add_product_to_page(product, x, y)

    c.save()
    print(f"PDF creado: {pdf_filename}")
    return pdf_filename







# Mostrar categorías disponibles
print("Categorías disponibles:")
for i, category in enumerate(classified_products.keys(), 1):
    print(f"{i}. {category}")

# Pedir al usuario que elija una categoría
category_choice = int(input("\nElija el número de la categoría: ")) - 1
selected_category = list(classified_products.keys())[category_choice]

# Mostrar tallas disponibles para la categoría seleccionada
print(f"\nTallas disponibles para {selected_category}:")
available_sizes = set(classified_products[selected_category].keys())
for size in available_sizes:
    print(size)

# Pedir al usuario que elija una talla
selected_size = input("\nElija una talla: ").upper()

# Mostrar productos que coinciden con la categoría y talla seleccionadas
if selected_size in classified_products[selected_category]:
    matching_products = classified_products[selected_category][selected_size]
    print(f"\nProductos en la categoría '{selected_category}' y talla '{selected_size}':")
    for product in matching_products:
        print(f"\nNombre: {product['Name']}")
        print(f"SKU: {product['SKU']}")
        print(f"Color: {product['Attribute Pa Color']}")
        print(f"Precio: {product['Regular Price']}")
        print(f"Stock: {product['Stock']}")
        print(f"Imagen: {product['Thumbnail Id']}")
    
    # Crear PDF
    pdf_file = create_pdf(matching_products, selected_category, selected_size)
    print(f"\nSe ha creado un PDF con las imágenes de los productos: {pdf_file}")
else:
    print(f"No hay productos disponibles en la categoría '{selected_category}' y talla '{selected_size}'.")