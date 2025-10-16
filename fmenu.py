import tkinter as tk
from tkinter import ttk, messagebox
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import firebase_admin
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("agromax-73287-firebase-adminsdk-fbsvc-5fb6496632.json")
firebase_admin.initialize_app(cred)



class AgroMaxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agro.Max - Sistema de Ventas")
        self.root.geometry("900x600")
        self.root.config(bg="#C7F9CC")

        self.facturas = [
            {"id": "F001", "cliente": "Juan Pérez", "total": 45000},
            {"id": "F002", "cliente": "Ana Gómez", "total": 82000}
        ]

        self.crear_estilo()
        self.crear_panel_lateral()
        self.crear_area_principal()

    # ---------------- ESTILO ----------------
    def crear_estilo(self):
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#E9F7EF",
            foreground="#000000",
            rowheight=25,
            fieldbackground="#E9F7EF"
        )
        style.configure("Treeview.Heading", background="#40916C", foreground="white")

    # ---------------- PANEL LATERAL ----------------
    def crear_panel_lateral(self):
        self.panel = tk.Frame(self.root, bg="#22543D", width=200)
        self.panel.pack(side="left", fill="y")

        tk.Label(
            self.panel,
            text="Agro.Max",
            bg="#22543D",
            fg="white",
            font=("Roboto", 20, "bold")
        ).pack(pady=25)

        botones = [
            ("Inicio", self.mostrar_inicio),
            ("Caja", self.opcion_caja),
            ("Facturas", self.opcion_facturas),
            ("Administración", self.opcion_admin),
            ("Fiados", self.opcion_fiados),
            ("Reportes", self.opcion_reportes),
            ("Salir", self.root.quit)
        ]

        for texto, comando in botones:
            btn = tk.Button(
                self.panel,
                text=texto,
                font=("Roboto", 12, "bold"),
                bg="#2F855A",
                fg="white",
                activebackground="#38A169",
                activeforeground="white",
                bd=0,
                relief="flat",
                width=15,
                height=2,
                command=comando
            )
            btn.pack(pady=8)

    # ---------------- ÁREA PRINCIPAL ----------------
    def crear_area_principal(self):
        self.area = tk.Frame(self.root, bg="#C7F9CC")
        self.area.pack(fill="both", expand=True)

        self.logo_label = tk.Label(
            self.area,
            text="AGRO.MAX",
            bg="#C7F9CC",
            fg="#22543D",
            font=("Roboto", 36, "bold")
        )
        self.logo_label.pack(expand=True)

    # ---------------- OPCIONES ----------------
    def mostrar_inicio(self):
        for widget in self.area.winfo_children():
            widget.destroy()
        tk.Label(
            self.area,
            text="Bienvenido a Agro.Max",
            bg="#C7F9CC",
            fg="#22543D",
            font=("Roboto", 26, "bold")
        ).pack(expand=True)

    def opcion_caja(self):
        messagebox.showinfo("Caja", "Aquí irá la sección de Caja")

    def opcion_admin(self):
        messagebox.showinfo("Administración", "Aquí irá el módulo administrativo")

    def opcion_fiados(self):
        messagebox.showinfo("Fiados", "Aquí se controlarán los fiados")

    def opcion_reportes(self):
        messagebox.showinfo("Reportes", "Aquí se generarán los reportes")

    # ---------------- FACTURAS ----------------
    def opcion_facturas(self):
        for widget in self.area.winfo_children():
            widget.destroy()

        tk.Label(
            self.area,
            text="Historial de Facturas",
            bg="#C7F9CC",
            fg="#22543D",
            font=("Roboto", 20, "bold")
        ).pack(pady=10)

        columnas = ("ID", "Cliente", "Total")
        tabla = ttk.Treeview(self.area, columns=columnas, show="headings", height=8)
        tabla.pack(pady=10)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=200, anchor="center")

        for factura in self.facturas:
            tabla.insert("", "end", values=(factura["id"], factura["cliente"], f"${factura['total']:,}"))

        def abrir_factura_pdf():
            seleccion = tabla.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Selecciona una factura para abrir.")
                return

            item = tabla.item(seleccion[0])
            datos = item["values"]
            self.crear_pdf(datos[0], datos[1], datos[2])

        tk.Button(
            self.area,
            text="Abrir Factura PDF",
            bg="#2F855A",
            fg="white",
            font=("Roboto", 12, "bold"),
            bd=0,
            width=20,
            height=2,
            command=abrir_factura_pdf
        ).pack(pady=15)

    # ---------------- CREAR PDF ----------------
    def crear_pdf(self, id_factura, cliente, total):
        nombre_pdf = f"{id_factura}.pdf"
        c = canvas.Canvas(nombre_pdf, pagesize=letter)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(200, 750, "Factura Agro.Max")
        c.setFont("Helvetica", 14)
        c.drawString(100, 700, f"ID: {id_factura}")
        c.drawString(100, 670, f"Cliente: {cliente}")
        c.drawString(100, 640, f"Total: {total}")
        c.line(100, 630, 500, 630)
        c.drawString(100, 600, "¡Gracias por preferir Agro.Max!")
        c.save()

        os.startfile(nombre_pdf)
        messagebox.showinfo("Factura", f"Factura {id_factura} generada correctamente.")

# ---------------- EJECUCIÓN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AgroMaxApp(root)
    root.mainloop()