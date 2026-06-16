from pathlib import Path
from typing import Dict, Any, List, Tuple

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from config import (
    PAGE_WIDTH,
    PAGE_HEIGHT,
    TEMPLATE_PATH,
    REFERENCE_IMAGE_WIDTH,
    REFERENCE_IMAGE_HEIGHT,
    FIELD_BOXES,
    DRAWING_REGIONS,
    SIGNATURE_BOX,
)


def _scale_factors():
    return PAGE_WIDTH / REFERENCE_IMAGE_WIDTH, PAGE_HEIGHT / REFERENCE_IMAGE_HEIGHT


def img_box_to_pdf(box: Tuple[float, float, float, float]):
    """Convierte (x,y,w,h) desde pixeles de imagen con origen arriba-izquierda
    a puntos PDF con origen abajo-izquierda."""
    sx, sy = _scale_factors()
    x, y, w, h = box
    return x * sx, PAGE_HEIGHT - (y + h) * sy, w * sx, h * sy


def draw_text_in_box(c: canvas.Canvas, text: str, box, font="Helvetica", size=8, bold=False):
    if text is None:
        return
    value = str(text).strip()
    if not value:
        return

    x, y, w, h = img_box_to_pdf(box)
    font_name = "Helvetica-Bold" if bold else font
    c.setFont(font_name, size)

    # Ajuste simple de tamaño si el texto excede el ancho.
    current_size = size
    while current_size > 5 and stringWidth(value, font_name, current_size) > w - 3:
        current_size -= 0.5
        c.setFont(font_name, current_size)

    c.drawString(x + 2, y + max(2, (h - current_size) / 2), value)


def draw_multiline_in_box(c: canvas.Canvas, text: str, box, font="Helvetica", size=7, leading=8):
    if text is None:
        return
    value = str(text).strip()
    if not value:
        return

    x, y, w, h = img_box_to_pdf(box)
    c.setFont(font, size)

    words = value.split()
    lines = []
    current = ""
    for word in words:
        proposed = (current + " " + word).strip()
        if stringWidth(proposed, font, size) <= w - 4:
            current = proposed
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    max_lines = max(1, int(h // leading))
    for idx, line in enumerate(lines[:max_lines]):
        c.drawString(x + 2, y + h - (idx + 1) * leading, line)


def draw_signature(c: canvas.Canvas, signature_path: str):
    if not signature_path:
        return
    path = Path(signature_path)
    if not path.exists():
        return
    x, y, w, h = img_box_to_pdf(SIGNATURE_BOX)
    try:
        c.drawImage(ImageReader(str(path)), x, y, w, h, mask="auto", preserveAspectRatio=True, anchor="c")
    except Exception:
        pass


def draw_strokes(c: canvas.Canvas, strokes_by_region: Dict[str, List[List[Tuple[float, float]]]]):
    if not strokes_by_region:
        return
    sx, sy = _scale_factors()
    c.setLineWidth(1.4)

    for region_name, strokes in strokes_by_region.items():
        region_box = DRAWING_REGIONS.get(region_name)
        if not region_box:
            continue
        region_x, region_y, _, _ = region_box

        for stroke in strokes:
            if len(stroke) < 2:
                continue

            # Los puntos se guardan relativos a la región, en pixeles de pantalla escalados
            # al tamaño real de la región de referencia.
            converted = []
            for px, py in stroke:
                image_x = region_x + px
                image_y = region_y + py
                converted.append((image_x * sx, PAGE_HEIGHT - image_y * sy))

            for p1, p2 in zip(converted, converted[1:]):
                c.line(p1[0], p1[1], p2[0], p2[1])


def generar_pdf(datos: Dict[str, Any], strokes_by_region, signature_path: str, output_path: str):
    output_path = str(output_path)
    c = canvas.Canvas(output_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # Fondo de contrato. Para máxima fidelidad usa un escaneo plano del formato vacío.
    if Path(TEMPLATE_PATH).exists():
        c.drawImage(ImageReader(str(TEMPLATE_PATH)), 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT)

    # Folio superior derecho
    folio = datos.get("folio", "")
    if folio:
        c.setFont("Helvetica-Bold", 13)
        c.drawRightString(PAGE_WIDTH - 35, PAGE_HEIGHT - 36, str(folio))

    for field, box in FIELD_BOXES.items():
        if field == "observaciones":
            draw_multiline_in_box(c, datos.get(field, ""), box)
        elif field in {"cantidad_letras", "fecha_lugar_devolucion"}:
            draw_text_in_box(c, datos.get(field, ""), box, size=7)
        else:
            draw_text_in_box(c, datos.get(field, ""), box, size=7.2)

    draw_strokes(c, strokes_by_region)
    draw_signature(c, signature_path)

    c.showPage()
    c.save()
    return output_path
