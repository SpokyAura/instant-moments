# sheets_utils.py

import gspread
from google.oauth2.service_account import Credentials
from config import SCOPES, SPREADSHEET_ID, HOJA_ACTIVA, CREDENTIALS_FILE

def conectar_sheets():
    """Conecta con Google Sheets y devuelve la hoja activa."""
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.worksheet(HOJA_ACTIVA)

def obtener_encabezados(worksheet):
    """Devuelve la fila de encabezados (primera fila)."""
    return worksheet.row_values(1)

def obtener_todas_las_filas(worksheet):
    """Devuelve todos los registros con encabezados como claves."""
    registros = worksheet.get_all_records(numericise_ignore=['all'])
    return registros

def escribir_en_celda(worksheet, fila, columna, valor):
    """Escribe un valor específico en una celda."""
    worksheet.update_cell(fila, columna, valor)

def obtener_contactos_pendientes(worksheet):
    """
    Devuelve la lista de contactos pendientes para mensajes o seguimiento.
    Ajusta las condiciones según tus reglas de negocio.
    """
    registros = obtener_todas_las_filas(worksheet)
    pendientes = []
    for registro in registros:
        # Ejemplo de filtro: pendientes si no tienen mensaje enviado o no tienen comentario de seguimiento
        mensaje_wa = registro.get("Mensaje enviado WA", "").strip()
        seguimiento = registro.get("Comentarios / Seguimiento", "").strip()
        if mensaje_wa == "" or seguimiento == "":
            pendientes.append(registro)
    return pendientes