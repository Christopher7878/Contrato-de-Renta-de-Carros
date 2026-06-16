import json
import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from PIL import Image, ImageTk, ImageGrab

from config import OUTPUT_DIR, FIELD_BOXES, DRAWING_REGIONS, TEMPLATE_PATH
from database import init_db, guardar_contrato, actualizar_pdf_folio, buscar_contratos
from pdf_generator import generar_pdf


FIELD_LABELS = {
    "nombre_completo": "Nombre completo",
    "referencia_1": "Referencia 1",
    "referencia_2": "Referencia 2",
    "domicilio_permanente": "Domicilio permanente",
    "ciudad_cliente": "Ciudad",
    "telefono_local": "Teléfono local",
    "celular": "Celular",
    "licencia_vence": "Licencia vence",
    "licencia_expedida": "Expedida",
    "tarjeta_credito": "Tarjeta de crédito",
    "fecha_vencimiento": "Fecha de vencimiento",
    "codigo": "Código",
    "autorizacion": "Autorización",
    "deposito": "Depósito",
    "identificacion_no": "Identificación No.",
    "conductor_adicional": "Conductor adicional o referencia",
    "licencia_no_adicional": "Licencia No.",
    "expedida_en_adicional": "Expedida en",
    "domicilio_adicional": "Domicilio adicional",
    "ciudad_adicional": "Ciudad adicional",
    "tel_adicional": "Tel. adicional",
    "fecha_dia": "Día",
    "fecha_mes": "Mes",
    "fecha_anio": "Año",
    "hora_salida": "Hora",
    "km_x_dia": "Km x día",
    "cargo_kilometro": "Cargo por kilómetro",
    "cargo_kilometro_importe": "Importe cargo km",
    "cargo_dia": "Cargo por día",
    "cargo_dia_importe": "Importe cargo día",
    "cargo_horas": "Cargo por horas",
    "cargo_horas_importe": "Importe cargo horas",
    "cargo_traslados": "Cargo por traslados",
    "cargo_traslados_importe": "Importe traslados",
    "otros_cargos": "Otros cargos",
    "otros_cargos_importe": "Importe otros cargos",
    "infraccion": "Infracción",
    "infraccion_importe": "Importe infracción",
    "anticipo": "Anticipo",
    "anticipo_importe": "Importe anticipo",
    "bloqueo": "Bloqueo",
    "bloqueo_importe": "Importe bloqueo",
    "total": "Total $",
    "cantidad_letras": "Cantidad con letras $",
    "recibi_auto_nombre": "Recibí el auto - nombre",
    "observaciones": "Observaciones",
    "carro": "Carro",
    "antena": "Antena",
    "placas": "Placas",
    "llanta": "Llanta",
    "marca": "Marca",
    "gato": "Gato",
    "color": "Color",
    "llave": "Llave",
    "motor": "Motor",
    "polvera": "Polvera",
    "stereo": "Stereo",
    "tapon_gas": "Tapón de gas",
    "reflejantes": "Reflejantes",
    "kilometraje_entrada": "Kilometraje entrada",
    "kilometraje_salida": "Kilometraje salida",
    "kilometraje_diferencia": "Kilometraje diferencia",
    "gas_porcentaje": "Gas %",
    "fecha_lugar_devolucion": "Fecha y lugar de devolución",
    "regresa_en": "Regresa en",
    "hora_devolucion": "Hora devolución",
    "contacto": "Contacto",
    "lugar_devolucion": "Lugar",
    "porcentaje_devolucion": "Porcentaje",
    "suma_diaria_danos": "Suma diaria por daños $",
    "pagare_dia": "Pagaré día",
    "pagare_mes": "Pagaré mes",
    "pagare_anio": "Pagaré año",
    "interes_moratorio": "Interés moratorio %",
}

CLIENT_FIELDS = [
    "nombre_completo", "referencia_1", "referencia_2",
    "domicilio_permanente", "ciudad_cliente",
    "telefono_local", "celular", "licencia_vence", "licencia_expedida",
    "tarjeta_credito", "fecha_vencimiento", "codigo", "autorizacion",
    "deposito", "identificacion_no",
    "conductor_adicional", "licencia_no_adicional", "expedida_en_adicional",
    "domicilio_adicional", "ciudad_adicional", "tel_adicional",
    "fecha_dia", "fecha_mes", "fecha_anio", "hora_salida",
]

VEHICLE_FIELDS = [
    "carro", "placas", "marca", "color", "motor", "stereo",
    "antena", "llanta", "gato", "llave", "polvera", "tapon_gas", "reflejantes",
    "kilometraje_entrada", "kilometraje_salida", "kilometraje_diferencia", "gas_porcentaje",
]

CHARGE_FIELDS = [
    "km_x_dia", "cargo_kilometro", "cargo_kilometro_importe",
    "cargo_dia", "cargo_dia_importe",
    "cargo_horas", "cargo_horas_importe",
    "cargo_traslados", "cargo_traslados_importe",
    "otros_cargos", "otros_cargos_importe",
    "infraccion", "infraccion_importe",
    "anticipo", "anticipo_importe",
    "bloqueo", "bloqueo_importe",
    "total", "cantidad_letras", "recibi_auto_nombre",
    "pagare_dia", "pagare_mes", "pagare_anio", "interes_moratorio",
    "suma_diaria_danos",
]

RETURN_FIELDS = [
    "fecha_lugar_devolucion", "regresa_en", "hora_devolucion",
    "contacto", "lugar_devolucion", "porcentaje_devolucion",
    "observaciones",
]


class DrawingBox(ttk.Frame):
    def __init__(self, master, title, region_name, width=420, height=160):
        super().__init__(master)
        self.region_name = region_name
        self.strokes = []
        self.current = []
        ttk.Label(self, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.canvas = tk.Canvas(self, width=width, height=height, bg="white", cursor="pencil")
        self.canvas.pack(fill="both", expand=True, pady=(4, 4))
        self.canvas.bind("<ButtonPress-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end)
        ttk.Button(self, text="Limpiar dibujo", command=self.clear).pack(anchor="e")

    def start(self, event):
        self.current = [(event.x, event.y)]

    def draw(self, event):
        if self.current:
            x1, y1 = self.current[-1]
            self.canvas.create_line(x1, y1, event.x, event.y, width=2)
            self.current.append((event.x, event.y))

    def end(self, event):
        if len(self.current) > 1:
            self.strokes.append(self.current)
        self.current = []

    def clear(self):
        self.canvas.delete("all")
        self.strokes.clear()

    def get_scaled_strokes(self):
        # Escala del canvas al tamaño real de la región en la foto de referencia.
        _, _, ref_w, ref_h = DRAWING_REGIONS[self.region_name]
        canvas_w = max(1, self.canvas.winfo_width())
        canvas_h = max(1, self.canvas.winfo_height())
        sx = ref_w / canvas_w
        sy = ref_h / canvas_h
        scaled = []
        for stroke in self.strokes:
            scaled.append([(round(x * sx, 2), round(y * sy, 2)) for x, y in stroke])
        return scaled


class SignatureBox(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="Firma del cliente", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.canvas = tk.Canvas(self, width=420, height=130, bg="white", cursor="pencil")
        self.canvas.pack(fill="x", expand=True, pady=(4, 4))
        self.last = None
        self.canvas.bind("<ButtonPress-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end)
        ttk.Button(self, text="Limpiar firma", command=self.clear).pack(anchor="e")

    def start(self, event):
        self.last = (event.x, event.y)

    def draw(self, event):
        if self.last:
            x1, y1 = self.last
            self.canvas.create_line(x1, y1, event.x, event.y, width=2)
            self.last = (event.x, event.y)

    def end(self, event):
        self.last = None

    def clear(self):
        self.canvas.delete("all")

    def save_png(self, path):
        # Método simple y local: captura el área visible del canvas.
        self.canvas.update()
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = x + self.canvas.winfo_width()
        h = y + self.canvas.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, w, h))
        img.save(path)
        return str(path)


class ContractApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Renta un Auto - Contratos digitales")
        self.geometry("1120x760")
        self.minsize(980, 650)
        init_db()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        self.vars = {}
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_cliente = ttk.Frame(self.notebook)
        self.tab_vehiculo = ttk.Frame(self.notebook)
        self.tab_cobros = ttk.Frame(self.notebook)
        self.tab_devolucion = ttk.Frame(self.notebook)
        self.tab_dibujo = ttk.Frame(self.notebook)
        self.tab_historial = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_cliente, text="Cliente y salida")
        self.notebook.add(self.tab_vehiculo, text="Vehículo")
        self.notebook.add(self.tab_cobros, text="Cobros")
        self.notebook.add(self.tab_devolucion, text="Devolución")
        self.notebook.add(self.tab_dibujo, text="Daños y firma")
        self.notebook.add(self.tab_historial, text="Historial")

        self.build_form_tab(self.tab_cliente, CLIENT_FIELDS, cols=3)
        self.build_form_tab(self.tab_vehiculo, VEHICLE_FIELDS, cols=3)
        self.build_form_tab(self.tab_cobros, CHARGE_FIELDS, cols=3)
        self.build_form_tab(self.tab_devolucion, RETURN_FIELDS, cols=2)

        self.build_drawing_tab()
        self.build_history_tab()
        self.build_bottom_bar()

    def build_form_tab(self, parent, fields, cols=3):
        outer = ttk.Frame(parent)
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        for i in range(cols):
            outer.columnconfigure(i, weight=1)

        for idx, field in enumerate(fields):
            row = idx // cols
            col = idx % cols
            frame = ttk.Frame(outer)
            frame.grid(row=row, column=col, sticky="ew", padx=8, pady=6)
            frame.columnconfigure(0, weight=1)

            ttk.Label(frame, text=FIELD_LABELS.get(field, field)).grid(row=0, column=0, sticky="w")

            if field == "observaciones":
                txt = tk.Text(frame, height=6, wrap="word")
                txt.grid(row=1, column=0, sticky="ew")
                self.vars[field] = txt
            else:
                var = tk.StringVar()
                ent = ttk.Entry(frame, textvariable=var)
                ent.grid(row=1, column=0, sticky="ew")
                self.vars[field] = var

    def build_drawing_tab(self):
        container = ttk.Frame(self.tab_dibujo)
        container.pack(fill="both", expand=True, padx=12, pady=12)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        info = ttk.Label(
            container,
            text=(
                "Dibuja rayones/golpes en las áreas correspondientes. "
                "Estos trazos se imprimen encima del croquis del contrato."
            ),
        )
        info.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.draw_auto = DrawingBox(container, "Condiciones del automóvil al salir", "danos_auto")
        self.draw_auto.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=8)

        self.draw_van = DrawingBox(container, "Condiciones de camioneta / vistas laterales", "danos_camioneta")
        self.draw_van.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=8)

        self.signature = SignatureBox(container)
        self.signature.grid(row=2, column=0, columnspan=2, sticky="ew", pady=14)

    def build_history_tab(self):
        top = ttk.Frame(self.tab_historial)
        top.pack(fill="x", padx=12, pady=12)

        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        ttk.Button(top, text="Buscar", command=self.load_history).pack(side="left", padx=8)
        ttk.Button(top, text="Abrir PDF seleccionado", command=self.open_selected_pdf).pack(side="left")

        columns = ("folio", "fecha", "cliente", "pdf")
        self.tree = ttk.Treeview(self.tab_historial, columns=columns, show="headings")
        self.tree.heading("folio", text="Folio")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("pdf", text="PDF")
        self.tree.column("folio", width=80, anchor="center")
        self.tree.column("fecha", width=160)
        self.tree.column("cliente", width=260)
        self.tree.column("pdf", width=500)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.load_history()

    def build_bottom_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(bar, text="Limpiar formulario", command=self.clear_form).pack(side="left")
        ttk.Button(bar, text="Generar PDF y guardar", command=self.save_contract).pack(side="right")

    def get_data(self):
        data = {}
        for field, widget in self.vars.items():
            if isinstance(widget, tk.Text):
                data[field] = widget.get("1.0", "end").strip()
            else:
                data[field] = widget.get().strip()
        return data

    def validate_data(self, data):
        required = ["nombre_completo", "telefono_local", "carro", "placas"]
        missing = [FIELD_LABELS[x] for x in required if not data.get(x)]
        if missing:
            messagebox.showwarning(
                "Datos incompletos",
                "Faltan campos recomendados:\n- " + "\n- ".join(missing)
            )
            return False
        return True

    def save_contract(self):
        data = self.get_data()
        if not self.validate_data(data):
            return

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        signature_tmp = OUTPUT_DIR / "firma_temporal.png"
        self.signature.save_png(signature_tmp)

        strokes = {
            "danos_auto": self.draw_auto.get_scaled_strokes(),
            "danos_camioneta": self.draw_van.get_scaled_strokes(),
        }

        # Primero reserva folio y registra en BD. Después se genera PDF con ese folio.
        placeholder_pdf = str(OUTPUT_DIR / "pendiente.pdf")
        folio = guardar_contrato(data, strokes, str(signature_tmp), placeholder_pdf)
        data["folio"] = folio

        pdf_path = OUTPUT_DIR / f"contrato_{folio}.pdf"
        generar_pdf(data, strokes, str(signature_tmp), str(pdf_path))
        actualizar_pdf_folio(folio, str(pdf_path))

        messagebox.showinfo("Contrato guardado", f"Contrato generado correctamente.\nFolio: {folio}\nPDF: {pdf_path}")
        self.load_history()
        self.open_file(pdf_path)

    def clear_form(self):
        if not messagebox.askyesno("Confirmar", "¿Quieres limpiar todos los campos?"):
            return
        for widget in self.vars.values():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
            else:
                widget.set("")
        self.draw_auto.clear()
        self.draw_van.clear()
        self.signature.clear()

    def load_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = buscar_contratos(self.search_var.get())
        for row in rows:
            try:
                data = json.loads(row["datos_json"])
            except Exception:
                data = {}
            self.tree.insert(
                "",
                "end",
                values=(
                    row["folio"],
                    row["fecha_creacion"],
                    data.get("nombre_completo", ""),
                    row["pdf_path"],
                ),
            )

    def open_selected_pdf(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Sin selección", "Selecciona un contrato en el historial.")
            return
        values = self.tree.item(selected[0], "values")
        pdf_path = values[3]
        self.open_file(pdf_path)

    def open_file(self, path):
        path = Path(path)
        if not path.exists():
            messagebox.showerror("Archivo no encontrado", f"No existe:\n{path}")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except Exception as exc:
            messagebox.showerror("No se pudo abrir", str(exc))


if __name__ == "__main__":
    app = ContractApp()
    app.mainloop()
