from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ASSETS_DIR = APP_DIR / "assets"
DATA_DIR = APP_DIR / "data"
OUTPUT_DIR = APP_DIR / "output"

DB_PATH = DATA_DIR / "contratos.sqlite3"
TEMPLATE_PATH = ASSETS_DIR / "contrato_base.jpg"

# Cambia este valor si quieres iniciar después del folio físico actual.
# Ejemplo: si el último folio impreso fue 4304, el primer contrato digital será 4305.
FOLIO_INICIAL = 4305

# Tamaño carta en puntos PDF: 8.5 x 11 in
PAGE_WIDTH = 612
PAGE_HEIGHT = 792

# Tamaño aproximado usado para calibrar coordenadas según la foto adjunta.
# Si reemplazas assets/contrato_base.jpg por un escaneo nuevo, ajusta coordenadas
# con calibrar_campos.py o edita FIELD_BOXES manualmente.
REFERENCE_IMAGE_WIDTH = 1024
REFERENCE_IMAGE_HEIGHT = 1365

# Cada campo se define con caja relativa a la imagen de referencia:
# (x, y, ancho, alto) en pixeles de la imagen. y se mide desde arriba.
# El generador convierte esas coordenadas a PDF automáticamente.
FIELD_BOXES = {
    "nombre_completo": (35, 235, 300, 26),
    "referencia_1": (360, 235, 280, 26),
    "referencia_2": (675, 235, 280, 26),

    "domicilio_permanente": (35, 268, 365, 26),
    "ciudad_cliente": (420, 268, 275, 26),

    "telefono_local": (35, 304, 210, 25),
    "celular": (285, 304, 170, 25),
    "licencia_vence": (505, 304, 210, 25),
    "licencia_expedida": (770, 304, 180, 25),

    "tarjeta_credito": (35, 340, 210, 25),
    "fecha_vencimiento": (275, 340, 200, 25),
    "codigo": (505, 340, 75, 25),
    "autorizacion": (610, 340, 120, 25),
    "deposito": (755, 340, 90, 25),
    "identificacion_no": (870, 340, 95, 25),

    "conductor_adicional": (35, 375, 285, 25),
    "licencia_no_adicional": (345, 375, 125, 25),
    "expedida_en_adicional": (490, 375, 115, 25),
    "domicilio_adicional": (620, 375, 120, 25),
    "ciudad_adicional": (750, 375, 90, 25),
    "tel_adicional": (855, 375, 100, 25),

    "fecha_dia": (371, 417, 38, 38),
    "fecha_mes": (419, 417, 42, 38),
    "fecha_anio": (470, 417, 43, 38),
    "hora_salida": (368, 472, 125, 22),

    "km_x_dia": (42, 690, 200, 23),
    "cargo_kilometro": (252, 690, 135, 23),
    "cargo_kilometro_importe": (402, 690, 105, 23),
    "cargo_dia": (42, 725, 200, 23),
    "cargo_dia_importe": (252, 725, 135, 23),
    "cargo_horas": (42, 760, 200, 23),
    "cargo_horas_importe": (252, 760, 135, 23),
    "cargo_traslados": (42, 795, 200, 23),
    "cargo_traslados_importe": (252, 795, 135, 23),
    "otros_cargos": (42, 830, 200, 23),
    "otros_cargos_importe": (252, 830, 135, 23),
    "infraccion": (42, 865, 200, 23),
    "infraccion_importe": (252, 865, 135, 23),
    "anticipo": (42, 900, 200, 23),
    "anticipo_importe": (252, 900, 135, 23),
    "bloqueo": (42, 935, 200, 23),
    "bloqueo_importe": (252, 935, 135, 23),
    "total": (42, 970, 345, 23),
    "cantidad_letras": (42, 1005, 460, 23),
    "recibi_auto_nombre": (150, 1035, 340, 23),
    "observaciones": (42, 1085, 460, 70),

    "carro": (610, 645, 145, 23),
    "antena": (835, 645, 145, 23),
    "placas": (610, 678, 145, 23),
    "llanta": (835, 678, 145, 23),
    "marca": (610, 710, 145, 23),
    "gato": (835, 710, 145, 23),
    "color": (610, 743, 145, 23),
    "llave": (835, 743, 145, 23),
    "motor": (610, 775, 145, 23),
    "polvera": (835, 775, 145, 23),
    "stereo": (610, 808, 145, 23),
    "tapon_gas": (835, 808, 145, 23),
    "reflejantes": (835, 842, 145, 23),

    "kilometraje_entrada": (655, 912, 165, 23),
    "kilometraje_salida": (655, 942, 165, 23),
    "kilometraje_diferencia": (655, 972, 165, 23),
    "gas_porcentaje": (905, 1005, 65, 23),

    "fecha_lugar_devolucion": (575, 1068, 245, 25),
    "regresa_en": (575, 1110, 250, 25),
    "hora_devolucion": (872, 1110, 82, 25),
    "contacto": (575, 1145, 250, 25),
    "lugar_devolucion": (575, 1180, 250, 25),
    "porcentaje_devolucion": (870, 1180, 90, 25),

    "suma_diaria_danos": (675, 1232, 150, 25),

    "pagare_dia": (350, 1198, 35, 20),
    "pagare_mes": (405, 1198, 75, 20),
    "pagare_anio": (495, 1198, 55, 20),
    "interes_moratorio": (435, 1245, 60, 20),
}

# Regiones para dibujar con mouse.
# El usuario puede marcar rayones/golpes encima del croquis; se guardan como trazos.
DRAWING_REGIONS = {
    "danos_auto": (55, 455, 440, 210),
    "danos_camioneta": (555, 405, 410, 220),
}

SIGNATURE_BOX = (170, 1284, 270, 42)
