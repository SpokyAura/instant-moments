import gspread
from google.oauth2.service_account import Credentials
from config import SCOPES, SPREADSHEET_ID, HOJA_ACTIVA, CREDENTIALS_FILE, COLUMNAS
from logger_config import logger

TRUE_VALUES = {True, "TRUE", "True", "1", 1, "Sí", "Si", "sí", "si"}

def conectar_sheets():
    """Conecta con Google Sheets y devuelve la hoja activa."""
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID)
        return sheet.worksheet(HOJA_ACTIVA)
    except Exception as e:
        logger.error(f"Error conectando con Google Sheets: {e}")
        return None

def obtener_encabezados(worksheet):
    """Devuelve la fila de encabezados (primera fila)."""
    try:
        return worksheet.row_values(1)
    except Exception as e:
        logger.error(f"Error obteniendo encabezados: {e}")
        return []

def obtener_todas_las_filas(worksheet):
    """Devuelve todos los registros con encabezados como claves."""
    try:
        registros = worksheet.get_all_records(numericise_ignore=['all'])
        return registros
    except Exception as e:
        logger.error(f"Error obteniendo filas: {e}")
        return []

def escribir_en_celda(worksheet, fila, columna, valor):
    """Escribe un valor específico en una celda."""
    try:
        worksheet.update_cell(fila, columna, valor)
    except Exception as e:
        logger.error(f"Error escribiendo en celda ({fila}, {columna}): {e}")

def obtener_contactos_pendientes(worksheet):
    """
    Devuelve la lista de contactos pendientes para mensajes o seguimiento.
    Ajusta las condiciones según tus reglas de negocio.
    """
    registros = obtener_todas_las_filas(worksheet)
    pendientes = []
    for registro in registros:
        try:
            mensaje_wa = registro.get("Mensaje enviado WA", "").strip()
            seguimiento = registro.get("Comentarios / Seguimiento", "").strip()
            if mensaje_wa == "" or seguimiento == "":
                pendientes.append(registro)
        except Exception as e:
            logger.warning(f"Error procesando registro para pendientes: {e}")
    return pendientes

def obtener_indices_columnas(worksheet):
    """
    Devuelve un diccionario de índices (1-based) de columnas,
    usando las claves de COLUMNAS como llaves.
    """
    indices = {}
    try:
        encabezados = worksheet.row_values(1)
        for clave, nombre_columna in COLUMNAS.items():
            try:
                indices[clave] = encabezados.index(nombre_columna) + 1
            except ValueError:
                logger.warning(f"No se encontró la columna '{nombre_columna}' en la hoja.")
                indices[clave] = None
    except Exception as e:
        logger.error(f"Error obteniendo encabezados para índices: {e}")
    return indices

def columna_a_letra(col_num):
    """Convierte índice de columna (1-based) a letra de columna Excel/Sheets."""
    letra = ''
    try:
        while col_num > 0:
            col_num, rem = divmod(col_num - 1, 26)
            letra = chr(65 + rem) + letra
    except Exception as e:
        logger.warning(f"Error convirtiendo número de columna a letra: {e}")
    return letra

def actualizar_interes_alto_batch(worksheet, contactos, columnas_idx):
    try:
        col_interes = columnas_idx.get("interes")
        col_respondio = columnas_idx.get("respondio")
        col_entrada_gratis = columnas_idx.get("entrada_gratis")

        if not all([col_interes, col_respondio, col_entrada_gratis]):
            logger.error("Columnas necesarias para actualizar interés no encontradas.")
            return

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
            logger.info("No hay filas para actualizar interés.")
            return

        body = {
            "valueInputOption": "USER_ENTERED",
            "data": celdas_a_actualizar
        }

        worksheet.spreadsheet.values_batch_update(body)
        logger.info(f"Actualizado interés a 'Alto' para {len(celdas_a_actualizar)} contactos.")

    except Exception as e:
        logger.error(f"Error actualizando interés alto batch: {e}")


def sincronizar_interes(worksheet, col_respondio_idx, col_interes_idx):
    """
    Recorre todos los registros en worksheet y sincroniza:
    si 'Respondió' está marcado, actualiza 'Interés' a 'Alto'.

    Args:
        worksheet: objeto de la hoja de cálculo.
        col_respondio_idx (int): índice de columna 'Respondió' (1-based).
        col_interes_idx (int): índice de columna 'Interés' (1-based).
    """
    try:
        registros = worksheet.get_all_records()
    except Exception as e:
        logger.error(f"Error obteniendo registros de la hoja: {e}")
        return

    for idx, registro in enumerate(registros, start=2):  # fila 1 es encabezado
        try:
            respondio_val = registro.get("Respondió")
            interes_val = registro.get("Interés", "")

            if respondio_val in TRUE_VALUES and interes_val != "Alto":
                worksheet.update_cell(idx, col_interes_idx, "Alto")
                logger.info(f"Actualizado Interés a Alto en fila {idx} por Respondió marcado.")
        except Exception as e:
            logger.warning(f"Error sincronizando fila {idx}: {e}")
