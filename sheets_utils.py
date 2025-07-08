# sheets_utils.py

import gspread
from google.oauth2.service_account import Credentials
from config import SCOPES, SPREADSHEET_ID, HOJA_ACTIVA, CREDENTIALS_FILE, COLUMNAS

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
        mensaje_wa = registro.get("Mensaje enviado WA", "").strip()
        seguimiento = registro.get("Comentarios / Seguimiento", "").strip()
        if mensaje_wa == "" or seguimiento == "":
            pendientes.append(registro)
    return pendientes

def obtener_indices_columnas(worksheet):
    """
    Devuelve un diccionario de índices (1-based) de columnas,
    usando las claves de COLUMNAS como llaves.
    """
    encabezados = worksheet.row_values(1)
    indices = {}
    for clave, nombre_columna in COLUMNAS.items():
        try:
            indices[clave] = encabezados.index(nombre_columna) + 1
        except ValueError:
            print(f"⚠️ No se encontró la columna '{nombre_columna}' en la hoja.")
            indices[clave] = None
    return indices

# Funciones secundarias usadas para actulizar en masa la hoja
def columna_a_letra(col_num):
    """Convierte índice de columna (1-based) a letra de columna Excel/Sheets."""
    letra = ''
    while col_num > 0:
        col_num, rem = divmod(col_num - 1, 26)
        letra = chr(65 + rem) + letra
    return letra

def actualizar_interes_alto_batch(worksheet, contactos, columnas_idx):
    col_interes = columnas_idx["interes"]
    col_respondio = columnas_idx["respondio"]
    col_entrada_gratis = columnas_idx["entrada_gratis"]

    celdas_a_actualizar = []
    for contacto in contactos:
        fila = contacto.get("fila")
        if not fila:
            continue
        
        respondio = str(contacto.get("Respondió", "")).strip().lower() == "true"
        entrada_gratis = str(contacto.get("Entrada Gratis", "")).strip().lower() == "true"

        if respondio or entrada_gratis:
            celdas_a_actualizar.append({
                "range": f"{columna_a_letra(col_interes)}{fila}",
                "values": [["Alto"]]
            })

    if not celdas_a_actualizar:
        print("No hay filas para actualizar interés.")
        return

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": celdas_a_actualizar
    }

    worksheet.spreadsheet.values_batch_update(body)
    print(f"✅ Actualizado interés a 'Alto' para {len(celdas_a_actualizar)} contactos.")