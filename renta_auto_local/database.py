import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from config import DB_PATH, DATA_DIR, FOLIO_INICIAL


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS folio_control (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            siguiente_folio INTEGER NOT NULL
        )
        """)
        conn.execute("""
        INSERT OR IGNORE INTO folio_control (id, siguiente_folio)
        VALUES (1, ?)
        """, (FOLIO_INICIAL,))
        conn.execute("""
        CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio INTEGER NOT NULL UNIQUE,
            fecha_creacion TEXT NOT NULL,
            datos_json TEXT NOT NULL,
            trazos_json TEXT,
            firma_png TEXT,
            pdf_path TEXT NOT NULL
        )
        """)
        conn.commit()


def reservar_folio(conn: sqlite3.Connection) -> int:
    # BEGIN IMMEDIATE bloquea escritura y evita folios duplicados.
    row = conn.execute("SELECT siguiente_folio FROM folio_control WHERE id = 1").fetchone()
    if row is None:
        conn.execute("INSERT INTO folio_control (id, siguiente_folio) VALUES (1, ?)", (FOLIO_INICIAL,))
        folio = FOLIO_INICIAL
    else:
        folio = int(row["siguiente_folio"])

    conn.execute(
        "UPDATE folio_control SET siguiente_folio = ? WHERE id = 1",
        (folio + 1,),
    )
    return folio


def guardar_contrato(
    datos: Dict[str, Any],
    trazos: Dict[str, List[List[tuple]]],
    firma_png: str,
    pdf_path: str,
) -> int:
    init_db()
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        folio = reservar_folio(conn)
        datos = dict(datos)
        datos["folio"] = folio
        conn.execute(
            """
            INSERT INTO contratos
            (folio, fecha_creacion, datos_json, trazos_json, firma_png, pdf_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                folio,
                datetime.now().isoformat(timespec="seconds"),
                json.dumps(datos, ensure_ascii=False),
                json.dumps(trazos, ensure_ascii=False),
                firma_png,
                pdf_path,
            ),
        )
        conn.commit()
        return folio
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def actualizar_pdf_folio(folio: int, pdf_path: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE contratos SET pdf_path = ? WHERE folio = ?",
            (pdf_path, folio),
        )
        conn.commit()


def buscar_contratos(texto: str = ""):
    init_db()
    with get_connection() as conn:
        if texto.strip():
            patron = f"%{texto.strip()}%"
            return conn.execute(
                """
                SELECT folio, fecha_creacion, datos_json, pdf_path
                FROM contratos
                WHERE CAST(folio AS TEXT) LIKE ?
                   OR datos_json LIKE ?
                ORDER BY folio DESC
                """,
                (patron, patron),
            ).fetchall()
        return conn.execute(
            """
            SELECT folio, fecha_creacion, datos_json, pdf_path
            FROM contratos
            ORDER BY folio DESC
            LIMIT 200
            """
        ).fetchall()
