import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from config import TEMPLATE_PATH, FIELD_BOXES, REFERENCE_IMAGE_WIDTH, REFERENCE_IMAGE_HEIGHT

"""
Herramienta opcional para ajustar coordenadas.

Uso:
1. Ejecuta: python calibrar_campos.py
2. Elige un campo en la lista.
3. Arrastra con el mouse el rectángulo donde debe imprimirse el dato.
4. Copia la salida que aparece abajo y pégala en config.py dentro de FIELD_BOXES.

Esto sirve cuando reemplazas assets/contrato_base.jpg por un escaneo mejor.
"""

class Calibrator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calibrador de campos")
        self.geometry("1200x800")

        self.img = Image.open(TEMPLATE_PATH)
        self.img_ratio = self.img.width / self.img.height
        self.display_h = 720
        self.display_w = int(self.display_h * self.img_ratio)
        self.scale_x = self.img.width / self.display_w
        self.scale_y = self.img.height / self.display_h
        self.tk_img = ImageTk.PhotoImage(self.img.resize((self.display_w, self.display_h)))

        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=8, pady=8)
        right = ttk.Frame(self)
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        self.field_var = tk.StringVar(value=list(FIELD_BOXES.keys())[0])
        self.combo = ttk.Combobox(left, values=list(FIELD_BOXES.keys()), textvariable=self.field_var, width=35)
        self.combo.pack(fill="x")
        ttk.Button(left, text="Copiar coordenada actual", command=self.print_current).pack(fill="x", pady=8)

        self.output = tk.Text(left, width=48, height=20)
        self.output.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(right, width=self.display_w, height=self.display_h, bg="gray")
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        self.start = None
        self.rect = None
        self.current_box = None
        self.canvas.bind("<ButtonPress-1>", self.on_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_end)

    def on_start(self, event):
        self.start = (event.x, event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red", width=2)

    def on_drag(self, event):
        if self.start and self.rect:
            self.canvas.coords(self.rect, self.start[0], self.start[1], event.x, event.y)

    def on_end(self, event):
        x1, y1 = self.start
        x2, y2 = event.x, event.y
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        self.current_box = (
            round(x * self.scale_x),
            round(y * self.scale_y),
            round(w * self.scale_x),
            round(h * self.scale_y),
        )
        self.print_current()

    def print_current(self):
        if not self.current_box:
            messagebox.showinfo("Sin selección", "Arrastra un rectángulo primero.")
            return
        field = self.field_var.get()
        line = f'    "{field}": {self.current_box},\n'
        self.output.insert("end", line)
        self.output.see("end")
        self.clipboard_clear()
        self.clipboard_append(line)

if __name__ == "__main__":
    Calibrator().mainloop()
