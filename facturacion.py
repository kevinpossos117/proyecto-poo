# agromax_reportes_integrado.py
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from io import BytesIO

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Imagenes
from PIL import Image, ImageTk

# Firebase
import firebase_admin
from firebase_admin import credentials, db

# FTP 
from ftplib import FTP, error_perm

# Graficas y Excel
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

try:
    import openpyxl
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except Exception:
    OPENPYXL_AVAILABLE = False

# ---------------- CONFIG - AJUSTA ESTAS RUTAS ----------------
SERVICE_ACCOUNT_PATH = "proyecto poo\\agromax-73287-firebase-adminsdk-fbsvc-be7daaf6c0.json"
DATABASE_URL = "https://agromax-73287-default-rtdb.firebaseio.com/"
LOGO_PATH = "proyecto poo\logo.jpg"
# FTP settings (opcional)
FTP_HOST = "127.0.0.1"
FTP_PORT = 21
FTP_USER = "perejil117"
FTP_PASS = "perejil117"
FTP_DIR = "Agromax"
# ------------------------------------------------------------

class AgroMaxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agro.Max - Sistema de Ventas")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)

        # Colores
        self.BG = "#B6D0A3"
        self.SIDEBAR = "#396855"
        self.ACCENT = "#74903A"
        self.root.config(bg=self.BG)

        # Cache imagenes
        self.product_images = {}

        # temporal upload
        self.foto_path_local = ""

        # Conectar Firebase con LAS RUTAS confirmadas
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
                firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
            # Rutas estandar que confirmaste:
            self.db_ref = db.reference("Productos")
            self.facturas_ref = db.reference("Facturas")
            self.fiados_ref = db.reference("Fiados")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar con Firebase:\n{e}")
            self.db_ref = None
            self.facturas_ref = None
            self.fiados_ref = None

        # UI
        self.crear_estilo()
        self.crear_panel_lateral()
        self.crear_area_principal()

    # ---------------- ESTILO ----------------
    def crear_estilo(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background="#E9F7EF", foreground="#000000", rowheight=24, fieldbackground="#E9F7EF")
        style.configure("Treeview.Heading", background=self.SIDEBAR, foreground="white")
        style.configure("Product.TButton", background="#E9F7EF", foreground=self.SIDEBAR, font=("Roboto", 10, "bold"))

    # ---------------- PANEL LATERAL ----------------
    def crear_panel_lateral(self):
        self.panel = tk.Frame(self.root, bg=self.SIDEBAR, width=220)
        self.panel.pack(side="left", fill="y")

        # Logo pequeño
        try:
            img = Image.open(LOGO_PATH)
            img = img.resize((64, 64))
            self.logo_small = ImageTk.PhotoImage(img)
            tk.Label(self.panel, image=self.logo_small, bg=self.SIDEBAR).pack(pady=(18, 6))
        except Exception:
            tk.Label(self.panel, text="", bg=self.SIDEBAR).pack(pady=(18, 6))

        tk.Label(self.panel, text="Agro.Max", bg=self.SIDEBAR, fg="white", font=("Roboto", 18, "bold")).pack(pady=(0, 20))

        botones = [
            ("Inicio", self.mostrar_inicio),
            ("Caja", self.opcion_caja),
            ("Inventario", self.opcion_inventario),
            ("Facturas", self.opcion_facturas),
            ("Administración", self.opcion_admin),
            ("Fiados", self.opcion_fiados),
            ("Reportes", self.opcion_reportes),   # <-- NUEVA pestaña de reportes (penúltima)
            ("Salir", self.root.quit)
        ]
        for texto, cmd in botones:
            b = tk.Button(self.panel, text=texto, font=("Roboto", 12, "bold"),
                          bg=self.ACCENT, fg="white", activebackground=self.SIDEBAR,
                          activeforeground="white", bd=0, relief="flat", width=18, height=2,
                          command=cmd)
            b.pack(pady=6)

    # ---------------- AREA PRINCIPAL ----------------
    def crear_area_principal(self):
        self.area = tk.Frame(self.root, bg=self.BG)
        self.area.pack(fill="both", expand=True)
        try:
            img = Image.open(LOGO_PATH)
            img = img.resize((280, 280))
            self.logo_big = ImageTk.PhotoImage(img)
            tk.Label(self.area, image=self.logo_big, bg=self.BG).pack(expand=True)
            tk.Label(self.area, text="AGRO.MAX", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 30, "bold")).pack(pady=(0, 30))
        except Exception:
            tk.Label(self.area, text="Bienvenido a Agro.Max", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 30, "bold")).pack(expand=True)

    def limpiar_area(self):
        for w in self.area.winfo_children():
            w.destroy()

    def mostrar_inicio(self):
        self.limpiar_area()
        try:
            tk.Label(self.area, image=self.logo_big, bg=self.BG).pack(pady=10)
        except Exception:
            pass
        tk.Label(self.area, text="Bienvenido a Agro.Max", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 26, "bold")).pack(pady=20)

    # ---------------- ADMIN (crud productos) ----------------
    def opcion_admin(self):
        self.limpiar_area()
        tk.Label(self.area, text="Gestión de Productos", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 20, "bold")).pack(pady=10)

        frame_form = tk.Frame(self.area, bg=self.BG)
        frame_form.pack(pady=8)

        tk.Label(frame_form, text="Código (lector):", bg=self.BG).grid(row=0, column=0, padx=6, pady=6, sticky="e")
        tk.Label(frame_form, text="Nombre:", bg=self.BG).grid(row=1, column=0, padx=6, pady=6, sticky="e")
        tk.Label(frame_form, text="Precio:", bg=self.BG).grid(row=2, column=0, padx=6, pady=6, sticky="e")
        tk.Label(frame_form, text="Cantidad:", bg=self.BG).grid(row=3, column=0, padx=6, pady=6, sticky="e")
        tk.Label(frame_form, text="Descripción:", bg=self.BG).grid(row=4, column=0, padx=6, pady=6, sticky="e")
        tk.Label(frame_form, text="Ruta Foto (nombre):", bg=self.BG).grid(row=5, column=0, padx=6, pady=6, sticky="e")

        self.codigo_entry = tk.Entry(frame_form, width=30)
        self.nombre_entry = tk.Entry(frame_form, width=30)
        self.precio_entry = tk.Entry(frame_form, width=30)
        self.cantidad_entry = tk.Entry(frame_form, width=30)
        self.descripcion_entry = tk.Entry(frame_form, width=30)
        self.foto_path_var = tk.StringVar()
        self.foto_path_entry = tk.Entry(frame_form, width=30, textvariable=self.foto_path_var)

        self.codigo_entry.grid(row=0, column=1, padx=6)
        self.nombre_entry.grid(row=1, column=1, padx=6)
        self.precio_entry.grid(row=2, column=1, padx=6)
        self.cantidad_entry.grid(row=3, column=1, padx=6)
        self.descripcion_entry.grid(row=4, column=1, padx=6)
        self.foto_path_entry.grid(row=5, column=1, padx=6, sticky="w")

        tk.Button(frame_form, text="Seleccionar Foto", bg="#74903A", fg="white", command=self.seleccionar_foto_producto).grid(row=5, column=2, padx=6)
        self.lbl_imagen_sel = tk.Label(frame_form, text="Ninguna imagen seleccionada", bg=self.BG)
        self.lbl_imagen_sel.grid(row=5, column=3, padx=6, sticky="w")

        btn_frame = tk.Frame(frame_form, bg=self.BG)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10)
        tk.Button(btn_frame, text="Registrar", bg=self.ACCENT, fg="white", width=12, command=self.registrar_producto).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Modificar", bg="#B7791F", fg="white", width=12, command=self.modificar_producto).grid(row=0, column=1, padx=6)
        tk.Button(btn_frame, text="Eliminar", bg="#C53030", fg="white", width=12, command=self.eliminar_producto).grid(row=0, column=2, padx=6)
        tk.Button(btn_frame, text="Limpiar campos", bg="#999999", fg="white", width=12, command=self._limpiar_campos_admin).grid(row=0, column=3, padx=6)

        # Tabla
        self.tabla = ttk.Treeview(self.area, columns=("Código", "Nombre", "Precio", "Cantidad", "Descripción", "Ruta Foto"), show="headings", height=10)
        self.tabla.heading("Código", text="Código"); self.tabla.column("Código", anchor="center", width=80)
        self.tabla.heading("Nombre", text="Nombre"); self.tabla.column("Nombre", anchor="w", width=150)
        self.tabla.heading("Precio", text="Precio"); self.tabla.column("Precio", anchor="center", width=80)
        self.tabla.heading("Cantidad", text="Cantidad"); self.tabla.column("Cantidad", anchor="center", width=80)
        self.tabla.heading("Descripción", text="Descripción"); self.tabla.column("Descripción", anchor="w", width=200)
        self.tabla.heading("Ruta Foto", text="Ruta Foto"); self.tabla.column("Ruta Foto", anchor="w", width=1, stretch=tk.NO)
        self.tabla.pack(pady=12, padx=10, fill="x")

        def on_select(e):
            sel = self.tabla.selection()
            if not sel: return
            values = self.tabla.item(sel[0])["values"]
            self.codigo_entry.delete(0, tk.END); self.codigo_entry.insert(0, values[0])
            self.nombre_entry.delete(0, tk.END); self.nombre_entry.insert(0, values[1])
            self.precio_entry.delete(0, tk.END); self.precio_entry.insert(0, values[2])
            self.cantidad_entry.delete(0, tk.END); self.cantidad_entry.insert(0, values[3])
            descripcion = values[4] if len(values) > 4 else ""
            ruta_foto = values[5] if len(values) > 5 else ""
            self.descripcion_entry.delete(0, tk.END); self.descripcion_entry.insert(0, descripcion)
            self.foto_path_var.set(ruta_foto)
            self.foto_path_local = ""
            if ruta_foto:
                self.lbl_imagen_sel.config(text=ruta_foto)
            else:
                self.lbl_imagen_sel.config(text="Ninguna imagen seleccionada")

        self.tabla.bind("<<TreeviewSelect>>", on_select)
        self.cargar_productos()

    def seleccionar_foto_producto(self):
        ruta_archivo = filedialog.askopenfilename(title="Seleccionar Foto del Producto", filetypes=(("Imágenes", "*.png;*.jpg;*.jpeg"), ("Todos", "*.*")))
        if ruta_archivo:
            self.foto_path_local = ruta_archivo
            nombre_remote = self.upload_image_via_ftp(self.foto_path_local)
            if nombre_remote:
                self.foto_path_var.set(nombre_remote)
                self.lbl_imagen_sel.config(text=nombre_remote)
                messagebox.showinfo("Imagen subida", f"Imagen subida al FTP como: {nombre_remote}")
            else:
                messagebox.showwarning("FTP", "No se pudo subir la imagen al FTP.")

    def _limpiar_campos_admin(self):
        for entry in (self.codigo_entry, self.nombre_entry, self.precio_entry, self.cantidad_entry, self.descripcion_entry):
            entry.delete(0, tk.END)
        self.foto_path_var.set("")
        self.foto_path_local = ""
        self.lbl_imagen_sel.config(text="Ninguna imagen seleccionada")

    # ---------------- FTP ----------------
    def upload_image_via_ftp(self, local_path, remote_filename=None):
        if not os.path.exists(local_path):
            return None
        if remote_filename is None:
            remote_filename = os.path.basename(local_path)
        ftp = None
        try:
            ftp = FTP()
            ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
            ftp.login(FTP_USER, FTP_PASS)
            ftp.set_pasv(True)
            try:
                ftp.mkd(FTP_DIR)
            except error_perm:
                pass
            try:
                ftp.cwd(FTP_DIR)
            except Exception:
                pass
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {remote_filename}", f)
            ftp.quit()
            return remote_filename
        except Exception as e:
            try:
                if ftp:
                    ftp.quit()
            except:
                pass
            print("FTP upload error:", e)
            return None

    # ---------------- CRUD Productos ----------------
    def registrar_producto(self):
        codigo = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        precio = self.precio_entry.get().strip()
        cantidad = self.cantidad_entry.get().strip()
        descripcion = self.descripcion_entry.get().strip()
        ruta_foto_field = self.foto_path_var.get().strip()
        if not (codigo and nombre and precio and cantidad):
            messagebox.showwarning("Campos vacíos", "Completa al menos los campos principales.")
            return
        try:
            precio = float(precio)
            cantidad = int(cantidad)
        except:
            messagebox.showwarning("Error", "Precio o cantidad con formato incorrecto.")
            return
        if not self.db_ref:
            messagebox.showerror("Firebase", "No conectado a Firebase. No se puede registrar.")
            return
        final_ruta_foto = ruta_foto_field
        if self.foto_path_local:
            nombre_remote = self.upload_image_via_ftp(self.foto_path_local)
            if nombre_remote:
                final_ruta_foto = nombre_remote
            else:
                messagebox.showwarning("FTP", "No se pudo subir la imagen al servidor FTP. El producto se guardará sin imagen.")
                final_ruta_foto = ""
        try:
            self.db_ref.child(codigo).set({
                "codigo": codigo,
                "nombre": nombre,
                "precio": precio,
                "cantidad": cantidad,
                "descripcion": descripcion,
                "ruta_foto": final_ruta_foto
            })
            messagebox.showinfo("Éxito", f"Producto '{nombre}' registrado con código {codigo}.")
            self.cargar_productos()
            self._limpiar_campos_admin()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar:\n{e}")

    def modificar_producto(self):
        codigo = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        precio = self.precio_entry.get().strip()
        cantidad = self.cantidad_entry.get().strip()
        descripcion = self.descripcion_entry.get().strip()
        ruta_foto_field = self.foto_path_var.get().strip()
        if not (codigo and nombre and precio and cantidad):
            messagebox.showwarning("Campos vacíos", "Completa al menos los campos principales.")
            return
        if not self.db_ref:
            messagebox.showerror("Firebase", "No conectado a Firebase.")
            return
        try:
            precio = float(precio)
            cantidad = int(cantidad)
        except:
            messagebox.showwarning("Error", "Precio o cantidad con formato incorrecto.")
            return
        final_ruta_foto = ruta_foto_field
        if self.foto_path_local:
            nombre_remote = self.upload_image_via_ftp(self.foto_path_local)
            if nombre_remote:
                final_ruta_foto = nombre_remote
            else:
                messagebox.showwarning("FTP", "No se pudo subir la nueva imagen al servidor FTP. Se conservará la anterior (si existe).")
        try:
            self.db_ref.child(codigo).update({
                "nombre": nombre,
                "precio": precio,
                "cantidad": cantidad,
                "descripcion": descripcion,
                "ruta_foto": final_ruta_foto
            })
            messagebox.showinfo("Actualizado", f"Producto {codigo} actualizado.")
            self.cargar_productos()
            self._limpiar_campos_admin()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cargar_productos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        if not self.db_ref:
            return
        try:
            data = self.db_ref.get()
            if data:
                for codigo, info in data.items():
                    self.tabla.insert("", "end", values=(
                        codigo, info.get("nombre", ""), info.get("precio", 0), info.get("cantidad", 0),
                        info.get("descripcion", ""), info.get("ruta_foto", "")
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar inventario:\n{e}")

    def eliminar_producto(self):
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showwarning("Atención", "Ingresa el código del producto a eliminar.")
            return
        if not self.db_ref:
            messagebox.showerror("Firebase", "No conectado a Firebase.")
            return
        try:
            self.db_ref.child(codigo).delete()
            messagebox.showinfo("Eliminado", f"Producto {codigo} eliminado.")
            self.cargar_productos()
            self._limpiar_campos_admin()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- INVENTARIO (cards con imagenes) ----------------
    def mostrar_detalle_producto(self, producto):
        detalle_win = tk.Toplevel(self.root)
        detalle_win.title(f"Detalle: {producto.get('nombre','')}")
        detalle_win.geometry("400x350")
        detalle_win.config(bg=self.BG)
        detalle_win.resizable(False, False)
        tk.Label(detalle_win, text=producto.get('nombre',''), font=("Roboto", 16, "bold"), bg=self.BG, fg=self.SIDEBAR).pack(pady=10)
        try:
            precio_val = float(producto.get('precio', 0))
            tk.Label(detalle_win, text=f"Precio: ${precio_val:,.2f}", font=("Roboto", 12), bg=self.BG).pack(pady=5)
        except:
            tk.Label(detalle_win, text=f"Precio: {producto.get('precio','')}", font=("Roboto", 12), bg=self.BG).pack(pady=5)
        codigo = producto.get('codigo')
        if codigo in self.product_images:
            tk.Label(detalle_win, image=self.product_images[codigo], bg=self.BG).pack(pady=5)
        else:
            tk.Label(detalle_win, text="[Imagen no cargada]", bg=self.BG).pack(pady=5)
        tk.Label(detalle_win, text="Descripción:", font=("Roboto", 12, "underline"), bg=self.BG).pack(pady=(10, 0))
        desc_text = producto.get('descripcion', 'Descripción no disponible.')
        desc_frame = tk.Frame(detalle_win, padx=20, bg=self.BG)
        desc_frame.pack(fill='x', pady=5)
        desc_widget = tk.Text(desc_frame, wrap="word", height=4, width=40, font=("Roboto", 10), bg="#E9F7EF")
        desc_widget.insert("1.0", desc_text)
        desc_widget.config(state=tk.DISABLED)
        desc_widget.pack(fill='x')

    def opcion_inventario(self):
        self.limpiar_area()
        tk.Label(self.area, text="Inventario de Productos", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 20, "bold")).pack(pady=10)
        if not self.db_ref:
            tk.Label(self.area, text="No hay conexión a Firebase.", bg=self.BG, fg="red").pack()
            return
        canvas_scroll = tk.Canvas(self.area, bg=self.BG)
        canvas_scroll.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar = ttk.Scrollbar(self.area, orient="vertical", command=canvas_scroll.yview)
        scrollbar.pack(side="right", fill="y")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        content_frame = tk.Frame(canvas_scroll, bg=self.BG)
        content_frame.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=content_frame, anchor="nw", width=self.area.winfo_width()-30)
        def resize_content_frame(event):
            try:
                canvas_scroll.itemconfig(canvas_scroll.winfo_children()[0], width=event.width)
            except Exception:
                pass
        canvas_scroll.bind('<Configure>', resize_content_frame)
        try:
            data = self.db_ref.get()
            if not data:
                tk.Label(content_frame, text="Inventario vacío.", bg=self.BG).pack(pady=20)
                return
            col = 0; row = 0
            self.product_images.clear()
            for codigo, info in data.items():
                nombre = info.get("nombre", "N/A")
                try:
                    precio = float(info.get("precio", 0))
                except:
                    precio = info.get("precio", 0)
                ruta_foto = info.get("ruta_foto", "")
                product_frame = tk.Frame(content_frame, bg="#E9F7EF", bd=2, relief="groove")
                product_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                img_label = tk.Label(product_frame, bg="#E9F7EF", width=120, height=80)
                img_label.pack(pady=(5, 0))
                if ruta_foto:
                    try:
                        img = None
                        if os.path.exists(ruta_foto):
                            img = Image.open(ruta_foto)
                        else:
                            ftp = FTP()
                            ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
                            ftp.login(FTP_USER, FTP_PASS)
                            ftp.set_pasv(True)
                            try:
                                ftp.cwd(FTP_DIR)
                            except Exception:
                                pass
                            bio = BytesIO()
                            ftp.retrbinary(f"RETR {ruta_foto}", bio.write)
                            ftp.quit()
                            bio.seek(0)
                            img = Image.open(bio)
                        if img:
                            img = img.resize((80, 80))
                            photo_image = ImageTk.PhotoImage(img)
                            self.product_images[codigo] = photo_image
                            img_label.config(image=photo_image)
                            img_label.image = photo_image
                        else:
                            img_label.config(text="[Sin Foto]", fg="black")
                    except Exception:
                        img_label.config(text="[Foto Error]", fg="red")
                else:
                    img_label.config(text="[Sin Foto]", fg="black")
                tk.Label(product_frame, text=nombre, font=("Roboto", 12, "bold"), bg="#E9F7EF", fg=self.SIDEBAR).pack()
                tk.Label(product_frame, text=f"${precio:,.2f}", font=("Roboto", 11), bg="#E9F7EF").pack()
                btn_detalle = tk.Button(product_frame, text="Ver Descripción", bg=self.ACCENT, fg="white", command=lambda p=info: self.mostrar_detalle_producto(p))
                btn_detalle.pack(pady=(5, 10), padx=10)
                col += 1
                if col > 3:
                    col = 0; row += 1
            content_frame.update_idletasks()
            canvas_scroll.config(scrollregion=canvas_scroll.bbox("all"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el inventario:\n{e}")

    # ---------------- CAJA ----------------
    def opcion_caja(self):
        self.limpiar_area()
        tk.Label(self.area, text="Caja - Registrar Venta", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 20, "bold")).pack(pady=8)
        frame_inputs = tk.Frame(self.area, bg=self.BG)
        frame_inputs.pack(pady=6, padx=6, fill="x")
        tk.Label(frame_inputs, text="Código:", bg=self.BG).grid(row=0, column=0, padx=6, pady=6, sticky="e")
        codigo_entry = tk.Entry(frame_inputs, width=20); codigo_entry.grid(row=0, column=1, padx=6)
        tk.Label(frame_inputs, text="Buscar por nombre:", bg=self.BG).grid(row=0, column=2, padx=6, pady=6, sticky="e")
        nombre_entry = tk.Entry(frame_inputs, width=30); nombre_entry.grid(row=0, column=3, padx=6)
        columnas = ("Código", "Nombre", "Cantidad", "Precio", "Subtotal")
        tabla_carrito = ttk.Treeview(self.area, columns=columnas, show="headings", height=10)
        for col in columnas:
            tabla_carrito.heading(col, text=col); tabla_carrito.column(col, anchor="center", width=150)
        tabla_carrito.pack(pady=10, padx=10, fill="x")
        total_var = tk.StringVar(value="$0")
        lbl_total_frame = tk.Frame(self.area, bg=self.BG); lbl_total_frame.pack(pady=6)
        tk.Label(lbl_total_frame, text="Total:", bg=self.BG, font=("Roboto", 14, "bold")).grid(row=0, column=0)
        tk.Label(lbl_total_frame, textvariable=total_var, bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 16, "bold")).grid(row=0, column=1, padx=8)
        carrito = []
        def actualizar_total():
            total = sum(item["cantidad"] * item["precio"] for item in carrito)
            total_var.set(f"${total:,.2f}")
        def agregar_o_incrementar(codigo, nombre, precio):
            for item in carrito:
                if item["codigo"] == codigo:
                    item["cantidad"] += 1
                    for iid in tabla_carrito.get_children():
                        vals = tabla_carrito.item(iid)["values"]
                        if vals[0] == codigo:
                            new_sub = item["cantidad"] * item["precio"]
                            tabla_carrito.item(iid, values=(codigo, nombre, item["cantidad"], f"${item['precio']:,.2f}", f"${new_sub:,.2f}"))
                            break
                    actualizar_total()
                    return
            carrito.append({"codigo": codigo, "nombre": nombre, "cantidad": 1, "precio": precio})
            tabla_carrito.insert("", "end", values=(codigo, nombre, 1, f"${precio:,.2f}", f"${precio:,.2f}"))
            actualizar_total()
        def buscar_producto_codigo():
            codigo = codigo_entry.get().strip()
            if not codigo:
                messagebox.showwarning("Atención", "Ingresa un código.")
                return
            if not self.db_ref:
                messagebox.showerror("Firebase", "No conectado a Firebase.")
                return
            try:
                data = self.db_ref.child(codigo).get()
                if not data:
                    messagebox.showerror("No encontrado", f"Producto con código {codigo} no existe.")
                    return
                nombre = data.get("nombre", "Sin nombre")
                precio = float(data.get("precio", 0))
                stock = int(data.get("cantidad", 0))
                if stock <= 0:
                    messagebox.showwarning("Agotado", "No hay stock para este producto.")
                    return
                agregar_o_incrementar(codigo, nombre, precio)
                codigo_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        def buscar_producto_nombre():
            nombre_busq = nombre_entry.get().strip().lower()
            if not nombre_busq:
                messagebox.showwarning("Atención", "Ingresa un nombre.")
                return
            if not self.db_ref:
                messagebox.showerror("Firebase", "No conectado a Firebase.")
                return
            try:
                all_data = self.db_ref.get()
                if not all_data:
                    messagebox.showerror("No encontrado", "No hay productos en inventario.")
                    return
                encontrado = None
                for codigo, info in all_data.items():
                    if nombre_busq in str(info.get("nombre", "")).lower():
                        encontrado = (codigo, info)
                        break
                if not encontrado:
                    messagebox.showerror("No encontrado", "Producto no encontrado por nombre.")
                    return
                codigo, info = encontrado
                nombre = info.get("nombre", "Sin nombre")
                precio = float(info.get("precio", 0))
                stock = int(info.get("cantidad", 0))
                if stock <= 0:
                    messagebox.showwarning("Agotado", "No hay stock para este producto.")
                    return
                agregar_o_incrementar(codigo, nombre, precio)
                nombre_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        def generar_factura():
            if not carrito:
                messagebox.showwarning("Atención", "No hay productos en la factura.")
                return
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            id_factura = f"F{ts}"
            total = sum(item["cantidad"] * item["precio"] for item in carrito)
            items_for_pdf = [(it["codigo"], it["nombre"], it["cantidad"], it["precio"]) for it in carrito]
            try:
                self._crear_pdf_con_items(id_factura, items_for_pdf, total)
            except Exception as e:
                messagebox.showerror("Error PDF", f"No se pudo crear el PDF:\n{e}")
                return
            factura_obj = {
                "id": id_factura,
                "fecha": datetime.now().isoformat(),
                "items": [{"codigo": it["codigo"], "nombre": it["nombre"], "cantidad": it["cantidad"], "precio": it["precio"]} for it in carrito],
                "total": total
            }
            if self.facturas_ref:
                try:
                    self.facturas_ref.child(id_factura).set(factura_obj)
                except Exception as e:
                    messagebox.showwarning("Advertencia", f"Factura generada pero no guardada en Firebase:\n{e}")
            if self.db_ref:
                try:
                    for it in carrito:
                        codigo = it["codigo"]; vendido = it["cantidad"]
                        nodo = self.db_ref.child(codigo)
                        current = nodo.get()
                        if current:
                            nuevo = int(current.get("cantidad", 0)) - vendido
                            if nuevo < 0: nuevo = 0
                            nodo.update({"cantidad": nuevo})
                except Exception as e:
                    messagebox.showwarning("Advertencia", f"Factura generada pero no se actualizó inventario:\n{e}")
            carrito.clear()
            for iid in tabla_carrito.get_children():
                tabla_carrito.delete(iid)
            actualizar_total()
            messagebox.showinfo("Factura", f"Factura {id_factura} generada correctamente.")
        btns_frame = tk.Frame(frame_inputs, bg=self.BG)
        btns_frame.grid(row=1, column=0, columnspan=4, pady=6)
        tk.Button(btns_frame, text="Buscar por código", bg=self.ACCENT, fg="white", command=buscar_producto_codigo).grid(row=0, column=0, padx=6)
        tk.Button(btns_frame, text="Buscar por nombre", bg=self.ACCENT, fg="white", command=buscar_producto_nombre).grid(row=0, column=1, padx=6)
        tk.Button(btns_frame, text="Generar Factura", bg="#2F855A", fg="white", width=18, height=2, command=generar_factura).grid(row=0, column=2, padx=12)

    # ---------------- PDF ----------------
    def _crear_pdf_con_items(self, id_factura, items, total):
        nombre_pdf = f"{id_factura}.pdf"
        c = canvas.Canvas(nombre_pdf, pagesize=letter)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(200, 750, "Factura Agro.Max")
        c.setFont("Helvetica", 11)
        c.drawString(50, 720, f"ID: {id_factura}")
        c.drawString(50, 700, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 680, "Código"); c.drawString(150, 680, "Nombre"); c.drawString(380, 680, "Cant."); c.drawString(430, 680, "Precio")
        y = 660
        c.setFont("Helvetica", 11)
        for codigo, nombre, cantidad, precio in items:
            c.drawString(50, y, str(codigo))
            c.drawString(150, y, str(nombre)[:30])
            c.drawString(380, y, str(cantidad))
            c.drawString(430, y, f"${precio:,.2f}")
            y -= 18
            if y < 70:
                c.showPage()
                c.setFont("Helvetica-Bold", 18)
                c.drawString(200, 750, "Factura Agro.Max")
                c.setFont("Helvetica", 11)
                c.drawString(50, 720, f"ID: {id_factura}")
                c.drawString(50, 700, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.setFont("Helvetica-Bold", 11)
                c.drawString(50, 680, "Código"); c.drawString(150, 680, "Nombre"); c.drawString(380, 680, "Cant."); c.drawString(430, 680, "Precio")
                y = 660
                c.setFont("Helvetica", 11)
        c.line(50, y - 6, 520, y - 6)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(350, y - 24, "Total:")
        c.drawString(430, y - 24, f"${total:,.2f}")
        c.save()
        try:
            os.startfile(nombre_pdf)
        except Exception:
            messagebox.showinfo("PDF creado", f"PDF guardado en: {os.path.abspath(nombre_pdf)}")

    # ---------------- FACTURAS (historial) ----------------
    def abrir_pdf_factura(self, tabla):
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una factura.")
            return
        id_factura = tabla.item(seleccion[0])["values"][0]
        nombre_pdf = f"{id_factura}.pdf"
        if not os.path.exists(nombre_pdf):
            messagebox.showerror("Error", f"El archivo PDF '{nombre_pdf}' no se encontró localmente.")
            return
        try:
            os.startfile(nombre_pdf)
        except Exception as e:
            messagebox.showerror("Error al abrir", f"No se pudo abrir el archivo PDF:\n{e}\n\nUbicación: {os.path.abspath(nombre_pdf)}")

    def opcion_facturas(self):
        self.limpiar_area()
        tk.Label(self.area, text="Historial de Facturas", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 20, "bold")).pack(pady=10)
        frame = tk.Frame(self.area, bg=self.BG)
        frame.pack(pady=8, padx=8, fill="x")
        columnas = ("ID", "Fecha", "Total")
        tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=12)
        tabla.pack(pady=8, padx=10, fill="x")
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center", width=300)
        tk.Button(frame, text="Abrir PDF (local)", bg=self.ACCENT, fg="white", command=lambda: self.abrir_pdf_factura(tabla)).pack(pady=6)
        if not self.facturas_ref:
            tk.Label(self.area, text="No hay conexión a Firebase para ver facturas.", bg=self.BG, fg="red").pack()
            return
        try:
            data = self.facturas_ref.get()
            if data:
                for fid, doc in data.items():
                    tabla.insert("", "end", values=(fid, doc.get("fecha", ""), f"${doc.get('total',0):,.2f}"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- FIADOS (simplificado) ----------------
    def opcion_fiados(self):
        self.limpiar_area()
        tk.Label(self.area, text="Registro de Fiados", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 20, "bold")).pack(pady=10)
        frame = tk.Frame(self.area, bg=self.BG); frame.pack(pady=10)
        tk.Label(frame, text="Nombre:", bg=self.BG).grid(row=0, column=0)
        self.nombre_fiado = tk.Entry(frame, width=25); self.nombre_fiado.grid(row=0, column=1, padx=5)
        tk.Label(frame, text="Deuda ($):", bg=self.BG).grid(row=1, column=0)
        self.valor_fiado = tk.Entry(frame, width=25); self.valor_fiado.grid(row=1, column=1, padx=5)
        tk.Label(frame, text="facturas :", bg=self.BG).grid(row=2, column=0)
        self.facturas_entry = tk.Entry(frame, width=25); self.facturas_entry.grid(row=2, column=1, padx=5)
        tk.Label(frame, text="Cantidad:", bg=self.BG).grid(row=3, column=0)
        self.cantidad_fiado = tk.Entry(frame, width=25); self.cantidad_fiado.grid(row=3, column=1, padx=5)
        tk.Button(frame, text="Agregar Fiao", command=self.agregar_fiado, bg="#27AE60", fg="white").grid(row=4, column=0, columnspan=2, pady=10)
        columnas = ("Nombre", "Deuda", "facturas", "Cantidad")
        self.tabla_fiados = ttk.Treeview(self.area, columns=columnas, show="headings", height=12)
        for col in columnas:
            self.tabla_fiados.heading(col, text=col); self.tabla_fiados.column(col, width=150)
        self.tabla_fiados.pack(pady=10)
        tk.Button(self.area, text="Eliminar seleccionado", bg="#E74C3C", fg="white", command=self.eliminar_fiado).pack(pady=5)
        self.tabla_fiados.bind("<Double-1>", self.editar_celda_fiado)
        self.cargar_fiados()

    def agregar_fiado(self):
        nombre = self.nombre_fiado.get()
        deuda = self.valor_fiado.get()
        facturas = self.facturas_entry.get()
        cantidad = self.cantidad_fiado.get()
        if not nombre or not deuda:
            messagebox.showwarning("Error", "El nombre y la deuda son obligatorios")
            return
        ref = db.reference("Fiados/" + nombre)
        ref.update({"deuda": deuda, "facturas": facturas, "cantidad": cantidad})
        self.cargar_fiados()
        self.nombre_fiado.delete(0, "end"); self.valor_fiado.delete(0, "end"); self.facturas_entry.delete(0, "end"); self.cantidad_fiado.delete(0, "end")

    def cargar_fiados(self):
        for fila in self.tabla_fiados.get_children():
            self.tabla_fiados.delete(fila)
        try:
            data = db.reference("Fiados").get() or {}
            for nombre, info in data.items():
                deuda = info.get("deuda", ""); facturas = info.get("facturas", ""); cantidad = info.get("cantidad", "")
                self.tabla_fiados.insert("", "end", values=(nombre, deuda, facturas, cantidad))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar fiados:\n{e}")

    def eliminar_fiado(self):
        seleccionado = self.tabla_fiados.selection()
        if not seleccionado:
            messagebox.showwarning("Error", "Seleccione un fiado para eliminar.")
            return
        item = seleccionado[0]
        nombre = self.tabla_fiados.item(item, "values")[0]
        confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar la factura '{nombre}'?")
        if not confirmar:
            return
        db.reference("Fiados/" + nombre).delete()
        self.tabla_fiados.delete(item)
        messagebox.showinfo("Eliminado", f"El fiado '{nombre}' fue eliminado.")

    def editar_celda_fiado(self, event):
        item = self.tabla_fiados.identify_row(event.y)
        columna = self.tabla_fiados.identify_column(event.x)
        col_index = int(columna.replace("#", "")) - 1
        if item:
            valor_actual = self.tabla_fiados.item(item, "values")[col_index]
            entry = tk.Entry(self.area)
            entry.insert(0, valor_actual)
            entry.focus()
            x, y, ancho, alto = self.tabla_fiados.bbox(item, columna)
            entry.place(x=x + self.tabla_fiados.winfo_x(), y=y + self.tabla_fiados.winfo_y(), width=ancho, height=alto)
            def guardar(event):
                nuevo = entry.get()
                valores = list(self.tabla_fiados.item(item, "values"))
                valores[col_index] = nuevo
                self.tabla_fiados.item(item, values=valores)
                entry.destroy()
                nombre = valores[0]
                ref = db.reference("Fiados/" + nombre)
                ref.update({"deuda": valores[1], "facturas": valores[2], "cantidad": valores[3]})
            entry.bind("<Return>", guardar)

    # ---------------- REPORTES ----------------
    def opcion_reportes(self):
        self.limpiar_area()
        tk.Label(self.area, text="Reportes - Ventas", bg=self.BG, fg=self.SIDEBAR, font=("Roboto", 20, "bold")).pack(pady=12)

        # Frame con controles y canvas
        ctrl_frame = tk.Frame(self.area, bg=self.BG)
        ctrl_frame.pack(pady=6, padx=8, fill="x")

        # Producto más vendido
        tk.Button(ctrl_frame, text="Producto más vendido", bg=self.ACCENT, fg="white", command=self.reporte_producto_mas_vendido).pack(side="left", padx=6)

        # Reporte semanal / mensual
        tk.Button(ctrl_frame, text="Reporte semanal (gráfica)", bg=self.ACCENT, fg="white", command=lambda: self.generar_reporte_periodo('week')).pack(side="left", padx=6)
        tk.Button(ctrl_frame, text="Reporte mensual (gráfica)", bg=self.ACCENT, fg="white", command=lambda: self.generar_reporte_periodo('month')).pack(side="left", padx=6)

        # Exportar a Excel (semana / mes)
        tk.Button(ctrl_frame, text="Exportar semanal a Excel", bg="#2F855A", fg="white", command=lambda: self.exportar_excel_periodo('week')).pack(side="left", padx=6)
        tk.Button(ctrl_frame, text="Exportar mensual a Excel", bg="#2F855A", fg="white", command=lambda: self.exportar_excel_periodo('month')).pack(side="left", padx=6)

        # Contenedor para gráfico/tabla
        self.report_container = tk.Frame(self.area, bg=self.BG)
        self.report_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Mensaje inicial
        tk.Label(self.report_container, text="Seleccione una acción para generar un reporte.", bg=self.BG).pack()

    def _obtener_facturas(self):
        """Obtiene facturas desde Firebase (dict) y devuelve lista de facturas con campos procesables."""
        if not self.facturas_ref:
            messagebox.showerror("Firebase", "No conectado a Firebase.")
            return []
        try:
            data = self.facturas_ref.get() or {}
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer facturas:\n{e}")
            return []
        facturas = []
        for fid, doc in data.items():
            fecha = doc.get("fecha")
            try:
                fecha_dt = datetime.fromisoformat(fecha)
            except Exception:
                # fallback si no es ISO
                try:
                    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    fecha_dt = None
            items = doc.get("items", [])
            total = float(doc.get("total", 0))
            facturas.append({"id": fid, "fecha": fecha_dt, "items": items, "total": total})
        return facturas

    def reporte_producto_mas_vendido(self):
        # limpia contenedor
        for w in self.report_container.winfo_children():
            w.destroy()
        facturas = self._obtener_facturas()
        if not facturas:
            tk.Label(self.report_container, text="No hay facturas para generar reporte.", bg=self.BG).pack()
            return
        # contar cantidades por codigo
        ventas = {}
        for f in facturas:
            for it in f["items"]:
                code = it.get("codigo")
                qty = int(it.get("cantidad", 0))
                ventas[code] = ventas.get(code, 0) + qty
        if not ventas:
            tk.Label(self.report_container, text="No hay items en facturas.", bg=self.BG).pack(); return
        # obtener max
        top_code = max(ventas, key=lambda k: ventas[k])
        top_qty = ventas[top_code]
        # obtener nombre del producto
        prod = None
        try:
            prod = self.db_ref.child(top_code).get() or {}
        except Exception:
            prod = {}
        nombre = prod.get("nombre", top_code)
        # mostrar info
        tk.Label(self.report_container, text=f"Producto más vendido: {nombre} (Código: {top_code})", bg=self.BG, font=("Roboto", 14, "bold")).pack(pady=8)
        tk.Label(self.report_container, text=f"Unidades vendidas: {top_qty}", bg=self.BG).pack(pady=4)
        # mostrar una pequeña tabla resumen
        cols = ("Código", "Nombre", "Vendidos")
        tbl = ttk.Treeview(self.report_container, columns=cols, show="headings", height=8)
        for c in cols:
            tbl.heading(c, text=c); tbl.column(c, anchor="center", width=180)
        tbl.pack(pady=8, fill="x")
        # ordenar top 10
        orden = sorted(ventas.items(), key=lambda kv: kv[1], reverse=True)
        for code, q in orden[:20]:
            try:
                p = self.db_ref.child(code).get() or {}
            except Exception:
                p = {}
            tbl.insert("", "end", values=(code, p.get("nombre", code), q))

    def generar_reporte_periodo(self, periodo: str):
        """periodo: 'week' or 'month' -> genera gráfica de ventas por producto en ese periodo"""
        for w in self.report_container.winfo_children():
            w.destroy()
        if not MATPLOTLIB_AVAILABLE:
            tk.Label(self.report_container, text="matplotlib no está disponible. Instala matplotlib para ver gráficas.", bg=self.BG).pack()
            return
        facturas = self._obtener_facturas()
        if not facturas:
            tk.Label(self.report_container, text="No hay facturas para generar reporte.", bg=self.BG).pack(); return
        # calcular rango
        ahora = datetime.now()
        if periodo == 'week':
            inicio = ahora - timedelta(days=7)
            titulo = "Reporte Semanal - Ventas por producto (últimos 7 días)"
        else:
            inicio = ahora - timedelta(days=30)
            titulo = "Reporte Mensual - Ventas por producto (últimos 30 días)"
        # acumular
        ventas = {}
        for f in facturas:
            if not f["fecha"]:
                continue
            if f["fecha"] >= inicio:
                for it in f["items"]:
                    code = it.get("codigo")
                    qty = int(it.get("cantidad", 0))
                    ventas[code] = ventas.get(code, 0) + qty
        if not ventas:
            tk.Label(self.report_container, text="No se encontraron ventas en el período seleccionado.", bg=self.BG).pack(); return
        # convertir a listas para graficar (top N)
        orden = sorted(ventas.items(), key=lambda kv: kv[1], reverse=True)[:12]
        labels = []
        valores = []
        for code, q in orden:
            try:
                p = self.db_ref.child(code).get() or {}
            except Exception:
                p = {}
            labels.append(p.get("nombre", code))
            valores.append(q)
        # crear figura matplotlib
        fig = Figure(figsize=(7,4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(range(len(labels)), valores)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylabel("Unidades vendidas")
        ax.set_title(titulo)
        fig.tight_layout()
        # insertar en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.report_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        # Mostrar tabla resumen debajo
        tbl_frame = tk.Frame(self.report_container, bg=self.BG)
        tbl_frame.pack(fill="x", pady=6)
        cols = ("Producto", "Vendidos")
        tabla = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=6)
        for c in cols:
            tabla.heading(c, text=c); tabla.column(c, anchor="center", width=300)
        tabla.pack(fill="x")
        for lbl, val in zip(labels, valores):
            tabla.insert("", "end", values=(lbl, val))

    def exportar_excel_periodo(self, periodo: str):
        """Genera un archivo Excel con ventas del periodo ('week'/'month')."""
        if not OPENPYXL_AVAILABLE:
            messagebox.showerror("openpyxl", "openpyxl no está instalado. Instala openpyxl para exportar a Excel.")
            return
        facturas = self._obtener_facturas()
        if not facturas:
            messagebox.showwarning("Sin datos", "No hay facturas para exportar.")
            return
        ahora = datetime.now()
        inicio = ahora - timedelta(days=7) if periodo == 'week' else ahora - timedelta(days=30)
        ventas = {}
        for f in facturas:
            if not f["fecha"]:
                continue
            if f["fecha"] >= inicio:
                for it in f["items"]:
                    code = it.get("codigo")
                    qty = int(it.get("cantidad", 0))
                    precio = float(it.get("precio", 0))
                    ventas.setdefault(code, {"cantidad": 0, "ingreso": 0.0})
                    ventas[code]["cantidad"] += qty
                    ventas[code]["ingreso"] += qty * precio
        if not ventas:
            messagebox.showwarning("Sin ventas", "No hay ventas en el período seleccionado.")
            return
        # crear workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        ws.append(["Código", "Producto", "Unidades Vendidas", "Ingreso"])
        for code, data in sorted(ventas.items(), key=lambda kv: kv[1]["cantidad"], reverse=True):
            try:
                prod = self.db_ref.child(code).get() or {}
            except Exception:
                prod = {}
            ws.append([code, prod.get("nombre", code), data["cantidad"], round(data["ingreso"],2)])
        nombre_archivo = f"reporte_{periodo}_{ahora.strftime('%Y%m%d%H%M%S')}.xlsx"
        try:
            wb.save(nombre_archivo)
            messagebox.showinfo("Exportado", f"Reporte exportado a {nombre_archivo}")
            # abrir carpeta o archivo si quieres (opcional)
            try:
                os.startfile(os.path.abspath(nombre_archivo))
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar Excel:\n{e}")

# ---------------- EJECUCIÓN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AgroMaxApp(root)
    root.mainloop()
