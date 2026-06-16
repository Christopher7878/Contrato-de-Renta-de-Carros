PROYECTO LOCAL: CONTRATO DIGITAL PARA RENTA DE AUTOS
======================================================

Este programa es local,. Funciona con:
- Python
- Tkinter para la interfaz
- SQLite para la base de datos
- ReportLab + Pillow para generar el PDF

ARCHIVOS
--------
app.py                 Programa principal.
database.py            Manejo de SQLite y folios únicos.
pdf_generator.py       Generación del PDF sobre la plantilla.
config.py              Configuración y coordenadas de campos.
calibrar_campos.py     Herramienta opcional para ajustar coordenadas.
assets/contrato_base.jpg  Plantilla visual del contrato.
data/contratos.sqlite3 Base de datos, se crea automáticamente.
output/                PDFs generados.

INSTALACIÓN EN WINDOWS
----------------------
1. Instala Python desde https://www.python.org/downloads/
   Activa la casilla "Add Python to PATH".
2. Abre CMD o PowerShell en esta carpeta.
3. Crea entorno virtual:
      python -m venv .venv
4. Activa entorno:
      .venv\Scripts\activate
5. Instala dependencias:
      pip install -r requirements.txt
6. Ejecuta:
      python app.py

INSTALACIÓN EN LINUX
--------------------
sudo apt install python3 python3-pip python3-venv python3-tk
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py

USO
---
1. Llena las pestañas Cliente, Vehículo, Cobros y Devolución.
2. Dibuja daños/rayones si aplica.
3. Firma en el recuadro.
4. Presiona "Generar PDF y guardar".
5. El programa:
   - reserva un folio único,
   - guarda datos en SQLite,
   - genera el PDF en output/,
   - registra la ruta del PDF en la base de datos.

FOLIOS
------
El primer folio se configura en config.py:
FOLIO_INICIAL = 4305

Si ya generaste contratos, no cambies manualmente la base de datos.
Cada folio se reserva dentro de una transacción SQLite para evitar duplicados.

IMPORTANTE SOBRE LA PLANTILLA
-----------------------------
La foto adjunta sirve para iniciar, pero para producción conviene reemplazar
assets/contrato_base.jpg por un escaneo limpio, recto, sin sombras y en blanco.

Después de reemplazar la imagen, ejecuta:
python calibrar_campos.py

Con esa herramienta puedes ajustar los rectángulos de impresión de cada campo.
