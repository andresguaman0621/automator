import csv
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

def normalize_column_name(name):
    return name.lower().strip().replace(" ", "_")

def load_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.json':
        return load_json_file(file_path)
    elif file_extension.lower() == '.csv':
        return load_csv_file(file_path)
    else:
        raise ValueError(f"Formato de archivo no soportado: {file_extension}")

def load_json_file(file_path):
    encodings = ['utf-8-sig', 'utf-8', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                data = json.load(file)
                return [{normalize_column_name(k): v for k, v in item.items()} for item in data]
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo decodificar el archivo con ninguna de las codificaciones: {encodings}")

def load_csv_file(file_path):
    encodings = ['utf-8-sig', 'utf-8', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                csv_reader = csv.DictReader(file)
                normalized_fieldnames = [normalize_column_name(name) for name in csv_reader.fieldnames]
                return [{normalize_column_name(k): v for k, v in row.items()} for row in csv_reader]
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo decodificar el archivo con ninguna de las codificaciones: {encodings}")

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

def optimize_image(img, max_size=(1300, 1300)):
    """Optimiza la imagen reduciéndola y comprimiéndola."""
    img.thumbnail(max_size)
    optimized_buffer = BytesIO()
    img.save(optimized_buffer, format='JPEG', quality=99, optimize=True)
    optimized_buffer.seek(0)
    return Image.open(optimized_buffer)

def download_and_optimize_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return optimize_image(img)

def create_pdf(products, category, size):
    pdf_filename = f"{category}_{size}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    space_between_rows = 3.5 * inch
    space_between_columns = 4 * inch

    def add_product_to_page(product, x, y):
        image_url = product.get('thumbnail_id', '')
        try:
            img = download_and_optimize_image(image_url)
            img_width, img_height = img.size
            aspect = img_height / float(img_width)
            
            display_width = 2.0 * inch
            display_height = display_width * aspect

            temp_filename = f"temp_image_{product.get('sku', '')}.jpg"
            img.save(temp_filename, "JPEG", quality=85, optimize=True)

            c.setFillColor(black)
            c.rect(x - 3, y - display_height - 5, display_width, display_height, fill=1)

            c.drawImage(temp_filename, x + 2, y - display_height, width=display_width, height=display_height)
            
            c.setStrokeColor(black)
            c.rect(x + 2, y - display_height, display_width, display_height, fill=0)

            c.setFont("Helvetica", 12)
            
            product_name = product.get('name', '').split('-')[0].strip()
            
            wrapped_lines = textwrap.wrap(product_name, width=15)
            text_y = y - 50
            for line in wrapped_lines:
                c.drawString(x + 2.35 * inch, text_y, line)
                text_y -= 14

            c.drawString(x + 2.35 * inch, y - 99, f"Color {product.get('attribute_pa_color', '')}")
            
            c.setFont("Helvetica-Bold", 15)
            c.drawString(x + 2.35 * inch, y - 120, f"{product.get('attribute_pa_talla', '')}")
            
            c.setFont("Helvetica", 12)
            c.drawString(x + 2.35 * inch, y - 168, f"Disponible: {product.get('stock', '')}")

            os.remove(temp_filename)

        except Exception as e:
            print(f"Error al procesar la imagen de {product.get('name', '')}: {e}")

    for i, product in enumerate(products):
        page_position = i % 6
        if page_position == 0 and i != 0:
            c.showPage()

        row = page_position // 2
        col = page_position % 2

        x = 0.5 * inch + col * space_between_columns
        y = height - (0.5 * inch + row * space_between_rows)

        add_product_to_page(product, x, y)

    c.save()
    print(f"PDF creado: {pdf_filename}")
    return pdf_filename

try:
    # file_path = input("Ingrese la ruta del archivo (JSON o CSV): ")
    file_path = "C:/Users/andy_/Downloads/stock2.json"
    data = load_file(file_path)
except ValueError as e:
    print(f"Error al cargar el archivo: {e}")
    exit(1)

# Clasificar productos
classified_products = {}
for product in data:
    stock = product.get('stock', '')
    if stock != "" and stock != "0":
        category = categorize_product(product.get('name', ''))
        talla = product.get('attribute_pa_talla', '')
        if category not in classified_products:
            classified_products[category] = {}
        if talla not in classified_products[category]:
            classified_products[category][talla] = []
        classified_products[category][talla].append(product)

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
        print(f"\nNombre: {product.get('name', '')}")
        print(f"SKU: {product.get('sku', '')}")
        print(f"Color: {product.get('attribute_pa_color', '')}")
        print(f"Precio: {product.get('regular_price', '')}")
        print(f"Stock: {product.get('stock', '')}")
        print(f"Imagen: {product.get('thumbnail_id', '')}")
    
    # Crear PDF
    pdf_file = create_pdf(matching_products, selected_category, selected_size)
    print(f"\nSe ha creado un PDF con las imágenes de los productos: {pdf_file}")
else:
    print(f"No hay productos disponibles en la categoría '{selected_category}' y talla '{selected_size}'.")
    