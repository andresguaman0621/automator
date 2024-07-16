import json
import requests
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

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

# categories = {
#     "Camiseta Oversize": ["Camiseta", "Oversize"],
#     "Camiseta Básica Oversize": ["Camiseta", "Básica", "Oversize"],
#     "Jogger": ["Jogger"],
#     "Hoodie Oversize": ["Hoodie", "Oversize"],
#     "Hoodie Oversize con Cierre": ["Hoodie", "Oversize", "Cierre"],
#     "Pantaloneta": ["Pantaloneta"],
#     "Hoodie Relaxed Fit": ["Hoodie", "Relaxed", "Fit"],
#     "Hoodie Básico Oversize": ["Hoodie", "Básico", "Oversize"]
# }


categories = {
    "Camiseta Oversize": ["Camiseta"],
    "Jogger": ["Jogger"],
    "Hoodie Oversize": ["Hoodie", "Oversize"],
    "Hoodie Oversize con Cierre": ["Hoodie", "Oversize", "Cierre"],
    "Pantaloneta": ["Pantaloneta"],
    "Hoodie Relaxed Fit": ["Hoodie", "Relaxed", "Fit"]
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

    for i, product in enumerate(products):
        image_url = product['Thumbnail Id']
        try:
            img = download_image(image_url)
            img_width, img_height = img.size
            aspect = img_height / float(img_width)
            
            # Ajustar el tamaño de la imagen para que quepa en la página
            display_width = width * 0.8  # 80% del ancho de la página
            display_height = display_width * aspect

            # Si la altura es mayor que el 80% de la altura de la página, ajustar
            if display_height > height * 0.8:
                display_height = height * 0.8
                display_width = display_height / aspect

            # Guardar la imagen como PNG temporal
            temp_filename = f"temp_image_{i}.png"
            img.save(temp_filename, "PNG")

            # Añadir la imagen al PDF
            c.drawImage(temp_filename, (width - display_width) / 2, height - display_height - 50, width=display_width, height=display_height)
            
            # Añadir información del producto
            c.setFont("Helvetica", 10)
            c.drawString(50, 50, f"Nombre: {product['Name']}")
            c.drawString(50, 35, f"SKU: {product['SKU']}")
            c.drawString(50, 20, f"Precio: {product['Regular Price']}")

            c.showPage()

            # Eliminar el archivo temporal
            os.remove(temp_filename)

        except Exception as e:
            print(f"Error al procesar la imagen de {product['Name']}: {e}")

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

# # Mostrar productos que coinciden con la categoría y talla seleccionadas
# if selected_size in classified_products[selected_category]:
#     print(f"\nProductos en la categoría '{selected_category}' y talla '{selected_size}':")
#     for product in classified_products[selected_category][selected_size]:
#         print(f"\nNombre: {product['Name']}")
#         print(f"SKU: {product['SKU']}")
#         print(f"Color: {product['Attribute Pa Color']}")
#         print(f"Precio: {product['Regular Price']}")
#         print(f"Stock: {product['Stock']}")
#         print(f"Imagen: {product['Thumbnail Id']}")
# else:
#     print(f"No hay productos disponibles en la categoría '{selected_category}' y talla '{selected_size}'.")


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