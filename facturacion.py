import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("C:\Users\Estudiante\Documents\programacion orientada a objetos\proyecto poo\agromax-73287-firebase-adminsdk-fbsvc-5fb6496632.json")
firebase_admin.initialize_app(cred)


class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal")
        self.root.geometry("400x300")

        # Botones del menú
        btn_facturas = tk.Button(root, text="Facturas", font=("Arial", 14),
                                 command=self.abrir_facturas, width=20, height=2)
        btn_facturas.pack(pady=20)

        btn_salir = tk.Button(root, text="Salir", font=("Arial", 14), command=root.quit,
                              width=20, height=2)
        btn_salir.pack(pady=20)

    def abrir_facturas(self):
        FacturasVentana()

class FacturasVentana:
    def __init__(self):
        self.win = tk.Toplevel()
        self.win.title("Historial de Facturas")
        self.win.geometry("500x400")

        tk.Label(self.win, text="Historial de Facturas", font=("Arial", 16, "bold")).pack(pady=10)

        # Listbox para mostrar facturas guardadas
        self.lista = tk.Listbox(self.win, width=50, height=15)
        self.lista.pack(pady=10)

        # Cargar facturas existentes
        self.cargar_facturas()

        # Botones
        frame_botones = tk.Frame(self.win)
        frame_botones.pack(pady=10)

        btn_ver = tk.Button(frame_botones, text="Ver Factura", command=self.ver_factura)
        btn_ver.grid(row=0, column=0, padx=10)

    def cargar_facturas(self):
        if not os.path.exists("facturas"):
            os.makedirs("facturas")

        archivos = os.listdir("facturas")
        for archivo in archivos:
            if archivo.endswith(".txt"):
                self.lista.insert(tk.END, archivo)

    def ver_factura(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione una factura")
            return

        archivo = self.lista.get(seleccion[0])
        with open(os.path.join("facturas", archivo), "r", encoding="utf-8") as f:
            contenido = f.read()

        # Mostrar en ventana aparte
        win_factura = tk.Toplevel(self.win)
        win_factura.title(f"Factura - {archivo}")
        win_factura.geometry("400x400")

        text_area = tk.Text(win_factura, wrap="word")
        text_area.insert("1.0", contenido)
        text_area.config(state="disabled")  # Solo lectura
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

# Guardar factura de prueba automáticamente
def guardar_factura_prueba():
    if not os.path.exists("facturas"):
        os.makedirs("facturas")
    nombre = datetime.now().strftime("factura_%Y%m%d_%H%M%S.txt")
    ruta = os.path.join("facturas", nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("----- FACTURA DE PRUEBA -----\nProducto X - $10,000\nTOTAL: $10,000")

# Ejecutar app
if __name__ == "__main__":
    guardar_factura_prueba()  # genera una factura de ejemplo
    root = tk.Tk()
    app = MenuPrincipal(root)
    root.mainloop()
