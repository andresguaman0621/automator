# import csv
# import json
# import requests
# from PIL import Image
# from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# import os
# from reportlab.lib.units import inch
# import textwrap
# from reportlab.lib.colors import black
# import ttkbootstrap as ttk
# from ttkbootstrap.constants import *
# from tkinter import PhotoImage, filedialog, messagebox

# def normalize_column_name(name):
#     return name.lower().strip().replace(" ", "_")

# def load_file(file_path):
#     _, file_extension = os.path.splitext(file_path)
    
#     if file_extension.lower() == '.json':
#         return load_json_file(file_path)
#     elif file_extension.lower() == '.csv':
#         return load_csv_file(file_path)
#     else:
#         raise ValueError(f"Formato de archivo no soportado: {file_extension}")

# def load_json_file(file_path):
#     encodings = ['utf-8-sig', 'utf-8', 'latin-1']
#     for encoding in encodings:
#         try:
#             with open(file_path, 'r', encoding=encoding) as file:
#                 data = json.load(file)
#                 return [{normalize_column_name(k): v for k, v in item.items()} for item in data]
#         except UnicodeDecodeError:
#             continue
#     raise ValueError(f"No se pudo decodificar el archivo con ninguna de las codificaciones: {encodings}")

# def load_csv_file(file_path):
#     encodings = ['utf-8-sig', 'utf-8', 'latin-1']
#     for encoding in encodings:
#         try:
#             with open(file_path, 'r', encoding=encoding) as file:
#                 csv_reader = csv.DictReader(file)
#                 normalized_fieldnames = [normalize_column_name(name) for name in csv_reader.fieldnames]
#                 return [{normalize_column_name(k): v for k, v in row.items()} for row in csv_reader]
#         except UnicodeDecodeError:
#             continue
#     raise ValueError(f"No se pudo decodificar el archivo con ninguna de las codificaciones: {encodings}")

# categories = {
#     "Camiseta Oversize": ["Camiseta"],
#     "Jogger": ["Jogger"],
#     "Hoodie Oversize": ["Hoodie", "Oversize Fit"],
#     "Hoodie Oversize con Cierre": ["Hoodie Oversize", "con Cierre"],
#     "Pantaloneta": ["Pantaloneta"],
#     "Hoodie Relaxed Fit": ["Hoodie", "Relaxed"]
# }

# def categorize_product(name):
#     name_lower = name.lower()
#     for category, keywords in categories.items():
#         if all(keyword.lower() in name_lower for keyword in keywords):
#             return category
#     return "Sin categoría"

# def optimize_image(img, max_size=(1300, 1300)):
#     """Optimiza la imagen reduciéndola y comprimiéndola."""
#     img.thumbnail(max_size)
#     optimized_buffer = BytesIO()
#     img.save(optimized_buffer, format='JPEG', quality=99, optimize=True)
#     optimized_buffer.seek(0)
#     return Image.open(optimized_buffer)

# def download_and_optimize_image(url):
#     response = requests.get(url)
#     img = Image.open(BytesIO(response.content))
#     return optimize_image(img)

# def create_pdf(products, category, size):
#     pdf_filename = f"{category}_{size}.pdf"
#     c = canvas.Canvas(pdf_filename, pagesize=letter)
#     width, height = letter

#     space_between_rows = 3.5 * inch
#     space_between_columns = 4 * inch

#     def add_product_to_page(product, x, y):
#         image_url = product.get('thumbnail_id', '')
#         try:
#             img = download_and_optimize_image(image_url)
#             img_width, img_height = img.size
#             aspect = img_height / float(img_width)
            
#             display_width = 2.0 * inch
#             display_height = display_width * aspect

#             temp_filename = f"temp_image_{product.get('sku', '')}.jpg"
#             img.save(temp_filename, "JPEG", quality=85, optimize=True)

#             c.setFillColor(black)
#             c.rect(x - 3, y - display_height - 5, display_width, display_height, fill=1)

#             c.drawImage(temp_filename, x + 2, y - display_height, width=display_width, height=display_height)
            
#             c.setStrokeColor(black)
#             c.rect(x + 2, y - display_height, display_width, display_height, fill=0)

#             c.setFont("Helvetica", 12)
            
#             product_name = product.get('name', '').split('-')[0].strip()
            
#             wrapped_lines = textwrap.wrap(product_name, width=15)
#             text_y = y - 50
#             for line in wrapped_lines:
#                 c.drawString(x + 2.35 * inch, text_y, line)
#                 text_y -= 14

#             c.drawString(x + 2.35 * inch, y - 99, f"Color {product.get('attribute_pa_color', '')}")
            
#             c.setFont("Helvetica-Bold", 15)
#             c.drawString(x + 2.35 * inch, y - 120, f"{product.get('attribute_pa_talla', '')}")
            
#             c.setFont("Helvetica", 12)
#             c.drawString(x + 2.35 * inch, y - 168, f"Disponible: {product.get('stock', '')}")

#             os.remove(temp_filename)

#         except Exception as e:
#             print(f"Error al procesar la imagen de {product.get('name', '')}: {e}")

#     for i, product in enumerate(products):
#         page_position = i % 6
#         if page_position == 0 and i != 0:
#             c.showPage()

#         row = page_position // 2
#         col = page_position % 2

#         x = 0.5 * inch + col * space_between_columns
#         y = height - (0.5 * inch + row * space_between_rows)

#         add_product_to_page(product, x, y)

#     c.save()
#     print(f"PDF creado: {pdf_filename}")
#     return pdf_filename

# class CatalogoApp(ttk.Window):
#     def __init__(self):
#         super().__init__(themename="sandstone")
#         self.title("Generador de Catálogo DUDS")
#         self.geometry("800x600")
#         self.data = None
#         self.classified_products = {}
#         self.selected_category = None
        
        
#         # Configurar el ícono para Windows
#         self.iconbitmap('C:/Users/andy_/Downloads/PROYECTO PYTHON/automator/logo.ico')

#         # Configurar el ícono para macOS
#         img = PhotoImage(file='C:/Users/andy_/Downloads/PROYECTO PYTHON/automator/logo.png')  # Usar PNG si no tienes .icns
#         self.iconphoto(True, img)
        
#         self.create_widgets()

#     def create_widgets(self):
#         # Frame principal
#         main_frame = ttk.Frame(self, padding="20")
#         main_frame.pack(fill=BOTH, expand=YES)

#         # Botón para cargar archivo
#         load_button = ttk.Button(main_frame, text="Cargar Archivo", command=self.load_file)
#         load_button.pack(pady=10)

#         # Combobox para seleccionar categoría
#         self.category_var = ttk.StringVar()
#         self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, state="readonly")
#         self.category_combo.pack(pady=10)
#         self.category_combo.bind("<<ComboboxSelected>>", self.update_sizes)

#         # Listbox para seleccionar tallas
#         self.size_listbox = ttk.Treeview(main_frame, selectmode="extended", show="tree")
#         self.size_listbox.pack(pady=10, fill=BOTH, expand=YES)

#         # Botón para generar PDF
#         generate_button = ttk.Button(main_frame, text="Generar PDF", command=self.generate_pdfs)
#         generate_button.pack(pady=10)

#     def load_file(self):
#         file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")])
#         if file_path:
#             try:
#                 self.data = load_file(file_path)
#                 self.classify_products()
#                 self.update_categories()
#                 messagebox.showinfo("Éxito", "Archivo cargado correctamente")
#             except Exception as e:
#                 messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")

#     def classify_products(self):
#         self.classified_products = {}
#         for product in self.data:
#             stock = product.get('stock', '')
#             if stock != "" and stock != "0":
#                 category = categorize_product(product.get('name', ''))
#                 talla = product.get('attribute_pa_talla', '')
#                 if category not in self.classified_products:
#                     self.classified_products[category] = {}
#                 if talla not in self.classified_products[category]:
#                     self.classified_products[category][talla] = []
#                 self.classified_products[category][talla].append(product)

#     def update_categories(self):
#         categories = list(self.classified_products.keys())
#         self.category_combo['values'] = categories
#         if categories:
#             self.category_combo.set(categories[0])
#             self.update_sizes()

#     def update_sizes(self, event=None):
#         self.selected_category = self.category_var.get()
#         sizes = list(self.classified_products[self.selected_category].keys())
#         self.size_listbox.delete(*self.size_listbox.get_children())
#         for size in sizes:
#             self.size_listbox.insert("", END, text=size)

#     def generate_pdfs(self):
#         selected_sizes = [self.size_listbox.item(item)["text"] for item in self.size_listbox.selection()]
#         if not selected_sizes:
#             messagebox.showwarning("Advertencia", "Por favor, seleccione al menos una talla")
#             return

#         for size in selected_sizes:
#             matching_products = self.classified_products[self.selected_category][size]
#             pdf_file = create_pdf(matching_products, self.selected_category, size)
#             messagebox.showinfo("Éxito", f"Se ha creado el PDF: {pdf_file}")

# if __name__ == "__main__":
#     app = CatalogoApp()
#     app.mainloop()


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
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import PhotoImage, filedialog, messagebox
from datetime import datetime

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
                return [{normalize_column_name(k): v for k, v in row.items()} for row in csv_reader]
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo decodificar el archivo con ninguna de las codificaciones: {encodings}")
categories = {
    "Camiseta Oversize": ["Camiseta", "Oversize"],
    "Camiseta Estampado Boxy Fit Original": ["Camiseta", "Boxy", "Fit", "Original"],
    "Camiseta Estampado Boxy Fit Premium": ["Camiseta", "Boxy", "Fit", "Premium"],
    "Jogger": ["Jogger"],
    "Hoodie Oversize": ["Hoodie", "Oversize Fit"],
    "Hoodie Oversize con Cierre": ["Hoodie Oversize", "con Cierre"],
    "Pantaloneta": ["Pantaloneta"],
    "Hoodie Relaxed Fit": ["Hoodie", "Relaxed"],
    "Pantalón": ["Pantalón", "Básico"]
}


def categorize_product(name):
    name_lower = name.lower()
    for category, keywords in categories.items():
        if all(keyword.lower() in name_lower for keyword in keywords):
            return category
    return "Sin categoría"

def optimize_image(img, max_size=(1300, 1300)):
    img.thumbnail(max_size)
    optimized_buffer = BytesIO()
    img.save(optimized_buffer, format='JPEG', quality=99, optimize=True)
    optimized_buffer.seek(0)
    return Image.open(optimized_buffer)

def download_and_optimize_image(url, max_retries=3, timeout=10):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return optimize_image(img)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error descargando imagen después de {max_retries} intentos: {url}")
                return Image.new('RGB', (800, 800), 'white')
            continue
        except Exception as e:
            print(f"Error procesando imagen: {url}")
            return Image.new('RGB', (800, 800), 'white')

def create_pdf(products, category, size):
    pdf_filename = f"{category}_{size}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    space_between_rows = 3.5 * inch
    space_between_columns = 4 * inch

    # Agregar fecha y hora en la primera página
    current_datetime = datetime.now().strftime("%d/%m/%Y (%H:%M)")
    c.setFont("Helvetica", 10)
    c.drawString(width - 130, height - 20, current_datetime)  # Ajuste para mover la fecha a la derecha

    def add_product_to_page(product, x, y):
        image_url = product.get('thumbnail_id', '')
        try:
            img = download_and_optimize_image(image_url)
            
            if img.size == (800, 800) and img.getpixel((0,0)) == (255,255,255):
                c.setFont("Helvetica", 10)
                c.drawString(x + 10, y - 30, "Error al cargar imagen")
            
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
            print(f"Error al procesar el producto {product.get('name', '')}: {e}")
            
    current_page = 0
    for i, product in enumerate(products):
        page_position = i % 6
        if page_position == 0 and i != 0:
            c.showPage()
            current_page += 1

        row = page_position // 2
        col = page_position % 2

        x = 0.5 * inch + col * space_between_columns
        y = height - (0.5 * inch + row * space_between_rows)

        add_product_to_page(product, x, y)

    c.save()
    return pdf_filename

class CatalogoApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="sandstone")
        self.title("Generador de Catálogo DUDS")
        self.geometry("800x600")
        self.data = None
        self.classified_products = {}
        self.selected_category = None
        
        try:
            self.iconbitmap('logo.ico')
            img = PhotoImage(file='logo.png')
            self.iconphoto(True, img)
        except:
            pass
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=BOTH, expand=YES)

        load_button = ttk.Button(main_frame, text="Cargar Archivo", command=self.load_file)
        load_button.pack(pady=10)

        self.category_var = ttk.StringVar()
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, state="readonly", width=40)
        self.category_combo.pack(pady=10)
        self.category_combo.bind("<<ComboboxSelected>>", self.update_sizes)

        self.size_listbox = ttk.Treeview(main_frame, selectmode="extended", show="tree")
        self.size_listbox.pack(pady=10, fill=BOTH, expand=YES)

        generate_button = ttk.Button(main_frame, text="Generar PDF", command=self.generate_pdfs)
        generate_button.pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")])
        if file_path:
            try:
                self.data = load_file(file_path)
                self.classify_products()
                self.update_categories()
                messagebox.showinfo("Éxito", "Archivo cargado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")

    def classify_products(self):
        self.classified_products = {}
        for product in self.data:
            stock = product.get('stock', '')
            if stock != "" and stock != "0":
                category = categorize_product(product.get('name', ''))
                talla = product.get('attribute_pa_talla', '')
                if category not in self.classified_products:
                    self.classified_products[category] = {}
                if talla not in self.classified_products[category]:
                    self.classified_products[category][talla] = []
                self.classified_products[category][talla].append(product)

    def update_categories(self):
        categories = list(self.classified_products.keys())
        self.category_combo['values'] = categories
        if categories:
            self.category_combo.set(categories[0])
            self.update_sizes()

    def update_sizes(self, event=None):
        self.selected_category = self.category_var.get()
        sizes = list(self.classified_products[self.selected_category].keys())
        self.size_listbox.delete(*self.size_listbox.get_children())
        for size in sizes:
            self.size_listbox.insert("", END, text=size)

    def generate_pdfs(self):
        selected_sizes = [self.size_listbox.item(item)["text"] for item in self.size_listbox.selection()]
        if not selected_sizes:
            messagebox.showwarning("Advertencia", "Por favor, seleccione al menos una talla")
            return

        generated_files = []  # Lista para guardar los nombres de los PDFs generados

        for size in selected_sizes:
            matching_products = self.classified_products[self.selected_category][size]
            pdf_file = create_pdf(matching_products, self.selected_category, size)
            generated_files.append(pdf_file)  # Agrega el PDF generado a la lista

        # Mostrar un solo mensaje cuando se hayan generado todos los PDFs
        if generated_files:
            messagebox.showinfo("Éxito", f"Se han creado los siguientes PDFs:\n" + "\n".join(generated_files))

if __name__ == "__main__":
    app = CatalogoApp()
    app.mainloop()
