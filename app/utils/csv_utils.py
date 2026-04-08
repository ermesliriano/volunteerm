import csv
import io
from typing import Dict, List, Tuple

EXPECTED_HEADERS = ["full_name", "email", "phone", "city", "availability", "notes"]

def parse_volunteers_csv(file_storage) -> Tuple[List[Dict[str, str]], List[str]]:
    errors: List[str] = []
    rows: List[Dict[str, str]] = []

    if not file_storage:
        return [], ["No se recibió fichero."]

    stream = io.TextIOWrapper(file_storage.stream, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(stream)

    if reader.fieldnames is None:
        return [], ["CSV sin cabecera (headers)."]

    headers = [h.strip() for h in reader.fieldnames if h is not None]
    missing = [h for h in EXPECTED_HEADERS if h not in headers]
    if missing:
        errors.append(f"Faltan columnas requeridas: {', '.join(missing)}")
        return [], errors

    for i, raw in enumerate(reader, start=2):
        rec = {k: (raw.get(k) or "").strip() for k in EXPECTED_HEADERS}
        if not rec["full_name"]:
            errors.append(f"Línea {i}: full_name vacío.")
            continue

        # Email opcional: '' -> ''
        # Luego en la capa de rutas se convierte '' -> None
        rows.append(rec)

    return rows, errors