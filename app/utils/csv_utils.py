import csv
import io
from typing import Dict, List, Tuple, Optional

EXPECTED_HEADERS = ["full_name", "email", "phone", "city", "availability", "notes"]

def parse_volunteers_csv(file_storage) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Parsea un CSV de voluntarios desde un FileStorage de Flask.
    Devuelve (rows, errors), donde rows es lista de dicts ya normalizados.
    """
    errors: List[str] = []
    rows: List[Dict[str, str]] = []

    if not file_storage:
        return [], ["No se recibió fichero."]

    # utf-8-sig maneja BOM
    stream = io.TextIOWrapper(file_storage.stream, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(stream)

    if reader.fieldnames is None:
        return [], ["CSV sin cabecera (headers)."]

    headers = [h.strip() for h in reader.fieldnames if h is not None]
    missing = [h for h in EXPECTED_HEADERS if h not in headers]
    if missing:
        errors.append(f"Faltan columnas requeridas: {', '.join(missing)}")

    if errors:
        return [], errors

    for i, raw in enumerate(reader, start=2):  # línea 1 es header
        try:
            rec = {k: (raw.get(k) or "").strip() for k in EXPECTED_HEADERS}

            if not rec["full_name"]:
                errors.append(f"Línea {i}: full_name vacío.")
                continue

            # Normalizar email vacío a ''
            if rec["email"] == "":
                rec["email"] = ""

            rows.append(rec)
        except Exception as ex:
            errors.append(f"Línea {i}: error al parsear fila ({ex}).")

    return rows, errors
