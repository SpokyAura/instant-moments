import csv
from datetime import datetime
from config import LOG_DATOS
from logger_config import logger

LOG_FILE = "log_fases.csv"

def inicializar_log():
    if not LOG_DATOS:
        return
    try:
        with open(LOG_FILE, mode='x', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Fecha", "Fase", "Mensajes Enviados", "Respuestas Recibidas", 
                "Entradas Gratis Entregadas", "Contactos sin Teléfono",
                "Ganadores sin Confirmar", "Porcentaje Conversión (%)", "Comentarios"
            ])
        logger.info(f"Archivo de log {LOG_FILE} inicializado.")
    except FileExistsError:
        logger.debug(f"Archivo de log {LOG_FILE} ya existe, no se inicializa.")
    except Exception as e:
        logger.error(f"Error al inicializar log: {e}", exc_info=True)

def registrar_estadistica(
    fase,
    mensajes_enviados,
    respuestas_recibidas,
    entradas_gratis,
    comentarios="",
    sin_numero=0,
    ganadores_no_confirmaron=0,
    porcentaje_conversion=None
):
    if not LOG_DATOS:
        return

    try:
        try:
            with open(LOG_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                filas = [row for row in reader if row["Fase"] != str(fase)]
        except FileNotFoundError:
            filas = []

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fila_log = {
            "Fecha": fecha,
            "Fase": str(fase),
            "Mensajes Enviados": str(mensajes_enviados),
            "Respuestas Recibidas": str(respuestas_recibidas),
            "Entradas Gratis Entregadas": str(entradas_gratis),
            "Contactos sin Teléfono": str(sin_numero),
            "Ganadores sin Confirmar": str(ganadores_no_confirmaron),
            "Porcentaje Conversión (%)": f"{porcentaje_conversion:.2f}" if porcentaje_conversion is not None else "",
            "Comentarios": comentarios
        }

        filas.append(fila_log)

        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
            campos = [
                "Fecha", "Fase", "Mensajes Enviados", "Respuestas Recibidas",
                "Entradas Gratis Entregadas", "Contactos sin Teléfono",
                "Ganadores sin Confirmar", "Porcentaje Conversión (%)", "Comentarios"
            ]
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(filas)

        # Log con formato bonito
        logger.info("📈 RESUMEN DE LA FASE:")
        logger.info(f"📅 Fecha de registro: {fecha}")
        logger.info(f"🌀 Fase: {fase}")
        logger.info(f"✉️ Mensajes enviados: {mensajes_enviados}")
        logger.info(f"✅ Respuestas recibidas: {respuestas_recibidas}")
        logger.info(f"🎟️ Entradas gratis entregadas: {entradas_gratis}")
        logger.info(f"📵 Contactos sin teléfono: {sin_numero}")
        logger.info(f"⏳ Ganadores sin confirmar asistencia: {ganadores_no_confirmaron}")
        if porcentaje_conversion is not None:
            logger.info(f"📊 Porcentaje de conversión: {porcentaje_conversion:.2f}%")
            if porcentaje_conversion < 25:
                logger.warning("⚠️ Advertencia: Conversión baja. Revisa el mensaje de convocatoria o tiempos de envío.")
        if comentarios:
            logger.info(f"🗒️ Comentarios: {comentarios}")
        logger.info(f"✅ Estadísticas registradas en {LOG_FILE}")

    except Exception as e:
        logger.error(f"Error al registrar estadísticas: {e}", exc_info=True)
