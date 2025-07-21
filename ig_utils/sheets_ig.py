# instagram_tools/sheets_ig.py
"""Funciones utilitarias para trabajar con la hoja *IG‑IM* en Google Sheets.

Este módulo se mantiene separado de `sheets_utils.py` para no mezclar lógica
específica de Instagram con la hoja CRM principal.
"""
from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Tuple

from config import (
    SCOPES,
    SPREADSHEET_ID,
    CREDENTIALS_FILE,
)
from logger_config import logger

# Encabezados esperados en la hoja IG‑IM
COLUMNAS_IG = {
    "nombre": "Nombre",
    "instagram": "Instagram",
    "check": "Check",
    "seguidores": "Seguidores",
}


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

def conectar_sheets_ig(nombre_hoja: str = "IG-IM"):
    """Devuelve el worksheet de la hoja *IG‑IM*.

    Args:
        nombre_hoja: Nombre de la pestaña en el spreadsheet.
    """
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = sheet.worksheet(nombre_hoja)
        logger.info("Conectado a la hoja IG‑IM")
        return worksheet
    except Exception as e:
        logger.error("Error conectando con hoja IG‑IM: %s", e, exc_info=True)
        return None


# ---------------------------------------------------------------------------
# Lectura y utilidades
# ---------------------------------------------------------------------------

def obtener_indices_columnas_ig(worksheet) -> Dict[str, int]:
    """Devuelve índices (1‑based) de los encabezados definidos en COLUMNAS_IG."""
    indices: Dict[str, int] = {}
    try:
        encabezados = worksheet.row_values(1)
        for clave, nombre in COLUMNAS_IG.items():
            try:
                indices[clave] = encabezados.index(nombre) + 1
            except ValueError:
                logger.warning("Columna '%s' no encontrada en IG‑IM", nombre)
                indices[clave] = None
    except Exception as e:
        logger.error("No se pudieron obtener encabezados IG‑IM: %s", e)
    return indices


def obtener_perfiles_instagram(worksheet, columnas_idx):
    """Devuelve lista de perfiles que aún no han sido verificados."""
    try:
        registros = worksheet.get_all_records(numericise_ignore=['all'])
        perfiles = []
        for i, row in enumerate(registros, start=2):  # start=2 porque encabezados están en fila 1
            usuario = str(row.get("Instagram", "")).strip()
            check = str(row.get("Check", "")).strip().lower()
            seguidores = str(row.get("Seguidores", "")).strip()

            # Saltar si no hay usuario
            if not usuario:
                continue

            # Saltar si ya fue revisado (Check tiene "sí", "no" o seguidores ya presentes)
            if check in {"sí", "si", "no"} or seguidores.isdigit():
                continue

            perfiles.append({
                "fila": i,
                "usuario": usuario,
            })
        return perfiles
    except Exception as e:
        logger.error(f"Error obteniendo perfiles de IG: {e}", exc_info=True)
        return []


# ---------------------------------------------------------------------------
# Escritura de resultados
# ---------------------------------------------------------------------------

def actualizar_perfil_resultado(
    worksheet,
    fila: int,
    col_check: int,
    col_seguidores: int,
    existe: bool,
    seguidores: int,
):
    """Actualiza una fila de IG‑IM con el resultado de verificación."""
    try:
        worksheet.update_cell(fila, col_check, "Sí" if existe else "No")
        if existe:
            worksheet.update_cell(fila, col_seguidores, seguidores)
    except Exception as e:
        logger.warning("Error actualizando fila %s IG‑IM: %s", fila, e, exc_info=True)
