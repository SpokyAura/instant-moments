import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

from config import (
    COLUMNAS,
    FASE_ACTUAL,
    CHROMEDRIVER_PATH,
    CHROME_PROFILE_PATH,
    ENVIAR_MENSAJES_INICIALES,
    ENVIAR_RECORDATORIOS_CONFIRMACION,
    ENVIAR_MENSAJES_INTEGRACION,
    ENVIAR_MENSAJES_RESULTADOS,
    REVISION_RESPUESTAS,
    LOG_DATOS,
    ACTIVAR_REVISION_IG
)

from sheets_utils import (
    conectar_sheets,
    obtener_todas_las_filas,
    obtener_indices_columnas,
    actualizar_interes_alto_batch,
    sincronizar_interes
)
from envio_mensajes import enviar_mensajes_contactos
from mensajes import (
    mensaje_convocatoria_inicial,
    mensaje_ganador_entrada,
    mensaje_cercano_a_ganador,
    mensaje_recordatorio_confirmacion,
    mensaje_integracion_futuras_fases,
)
from revisar_respuestas import revisar_respuestas
from log_fases import inicializar_log, registrar_estadistica


from logger_config import logger  # <--- Importamos el logger

inicializar_log()

def iniciar_driver():
    try:
        options = Options()
        options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("Driver de Chrome iniciado correctamente.")
        return driver
    except WebDriverException as e:
        logger.error(f"Error al iniciar el driver de Chrome: {e}", exc_info=True)
        return None

def validar_telefono(telefono):
    tel_str = str(telefono).strip()
    if not tel_str.isdigit() or len(tel_str) < 10:
        return False
    return True

def main():
    try:
        logger.info("Iniciando conexión con Google Sheets...")
        worksheet = conectar_sheets()
    except Exception as e:
        logger.error(f"Error conectando a Google Sheets: {e}", exc_info=True)
        return

    try:
        logger.info("Obteniendo contactos desde la hoja...")
        contactos = obtener_todas_las_filas(worksheet)
        if not contactos:
            logger.warning("No se encontraron contactos. Abortando ejecución.")
            return
        for i, contacto in enumerate(contactos, start=2):
            contacto["fila"] = i

        logger.info("Obteniendo índices de columnas...")
        columnas_idx = obtener_indices_columnas(worksheet)
        sincronizar_interes(worksheet, columnas_idx["respondio"], columnas_idx["interes"])

        logger.info("Actualizando interés a Alto para contactos con Respondió o Entrada Gratis...")
        actualizar_interes_alto_batch(worksheet, contactos, columnas_idx)
    except Exception as e:
        logger.error(f"Error procesando datos de contactos: {e}", exc_info=True)
        return

    try:
        logger.info("Iniciando Selenium WebDriver...")
        driver = iniciar_driver()
        if driver is None:
            logger.warning("No se pudo iniciar el driver de Chrome. Abortando.")
            return
    except Exception as e:
        logger.error(f"Error iniciando el driver de Selenium: {e}", exc_info=True)
        return

    try:
        # Filtros de contactos
        contactos_resultados_sin_pase = [
            c for c in contactos
            if str(c.get("Respondió", "")).lower() == "true"
            and str(c.get("Entrada Gratis", "")).lower() != "true"
            and c.get("Comentarios / Seguimiento", "").strip() == ""
        ]

        contactos_resultados_con_pase = [
            c for c in contactos
            if str(c.get("Respondió", "")).lower() == "true"
            and str(c.get("Entrada Gratis", "")).lower() == "true"
            and c.get("Comentarios / Seguimiento", "").strip() == ""
        ]

        contactos_ganadores_pendientes = [
            c for c in contactos
            if str(c.get("Respondió", "")).lower() == "true"
            and str(c.get("Entrada Gratis", "")).lower() == "true"
            and str(c.get("Correo Verificado", "")).lower() != "true"
            and str(c.get("Recordatorio Enviado", "")).lower() != "true"
        ]

        logger.info(f"Contactos sin pase detectados: {len(contactos_resultados_sin_pase)}")
        logger.info(f"Contactos con pase detectados: {len(contactos_resultados_con_pase)}")

        contactos_no_respondieron = [
            c for c in contactos if str(c.get("Respondió", "")).lower() != "true"
        ]
        contactos_ganadores_pendientes_confirmacion = [
            c for c in contactos
            if str(c.get("Respondió", "")).lower() == "true"
            and str(c.get("Entrada Gratis", "")).lower() == "true"
            and str(c.get("Confirmó Asistencia", "")).lower() != "sí"
        ]
        contactos_respondieron = [
            c for c in contactos if str(c.get("Respondió", "")).lower() == "true"
        ]
    except Exception as e:
        logger.error(f"Error filtrando contactos: {e}", exc_info=True)
        driver.quit()
        return

    try:
        if ENVIAR_MENSAJES_INICIALES:
            logger.info(f"Enviando mensajes de convocatoria inicial a {len(contactos_no_respondieron)} contactos...")
            enviar_mensajes_contactos(driver, worksheet, contactos_no_respondieron, FASE_ACTUAL, mensaje_convocatoria_inicial, columnas_idx)
        else:
            logger.info("Saltando envío de mensajes de convocatoria inicial.")

        if ENVIAR_MENSAJES_RESULTADOS:
            logger.info(f"Enviando mensaje a participantes sin pase ({len(contactos_resultados_sin_pase)})...")
            enviar_mensajes_contactos(driver, worksheet, contactos_resultados_sin_pase, FASE_ACTUAL, mensaje_cercano_a_ganador, columnas_idx, seguimiento="Participante sin pase")

            logger.info(f"Enviando mensaje a ganadores sin seguimiento ({len(contactos_resultados_con_pase)})...")
            enviar_mensajes_contactos(driver, worksheet, contactos_resultados_con_pase, FASE_ACTUAL, mensaje_ganador_entrada, columnas_idx, seguimiento="Ganador - Entrada Gratis", proxima_accion="Mandar mensaje Recordatorio de confirmación")
        else:
            logger.info("Saltando envío de mensajes de resultados.")

        if ENVIAR_RECORDATORIOS_CONFIRMACION:
            logger.info(f"Enviando recordatorio a ganadores pendientes ({len(contactos_ganadores_pendientes)})...")
            enviar_mensajes_contactos(driver, worksheet, contactos_ganadores_pendientes, FASE_ACTUAL, mensaje_recordatorio_confirmacion,
                columnas_idx,
                marcar_recordatorio=True
            )
        else:
            logger.info("Saltando envío de recordatorios de confirmación.")

        if REVISION_RESPUESTAS:
            logger.info("Revisando respuestas recibidas y asignando entradas gratis...")
            ganadores = revisar_respuestas(worksheet, COLUMNAS)
            logger.info(f"Ganadores asignados: {len(ganadores)} contactos.")
        else:
            logger.info("Saltando revisión automática de respuestas.")

        if ENVIAR_MENSAJES_INTEGRACION:
            logger.info(f"Enviando mensajes de integración a {len(contactos_respondieron)} contactos que respondieron...")
            enviar_mensajes_contactos(driver, worksheet, contactos_respondieron, FASE_ACTUAL, mensaje_integracion_futuras_fases, columnas_idx)
        else:
            logger.info("Saltando envío de mensajes de integración.")
    except Exception as e:
        logger.error(f"Error durante envío de mensajes o revisiones: {e}", exc_info=True)
    finally:
        logger.info("Cerrando driver de Selenium...")
        driver.quit()

    try:
        contactos_con_numero_invalido = [
            c for c in contactos
            if not validar_telefono(c.get("Teléfono", ""))
        ]

        if LOG_DATOS:
            contactos_enviados = [
                c for c in contactos
                if c.get("Mensaje enviado WA", "").strip() != "" and not str(c.get("Mensaje enviado WA", "")).lower().startswith("error")
            ]

            registrar_estadistica(
                fase=FASE_ACTUAL,
                mensajes_enviados=len(contactos_enviados),
                respuestas_recibidas=len(contactos_respondieron),
                entradas_gratis=sum(
                    1 for c in contactos_enviados
                    if str(c.get("Entrada Gratis", "")).lower() == "true"
                ),
                comentarios=f"Resumen fase {FASE_ACTUAL}"
            )
            logger.info(f"Estadísticas de fase {FASE_ACTUAL} registradas en log_fases.csv")
    except Exception as e:
        logger.error(f"Error al registrar estadísticas o procesar datos finales: {e}", exc_info=True)
        
    try:
        if ACTIVAR_REVISION_IG:
            logger.info("Iniciando revisión de perfiles de Instagram...")
            from ig_utils.verificar_perfiles import revisar_perfiles_instagram
            revisar_perfiles_instagram()
        else:
            logger.info("Revisión de perfiles IG desactivada por configuración.")
    except Exception as e:
        logger.error(f"Error al revisar perfiles de Instagram: {e}", exc_info=True)

if __name__ == "__main__":
    main()
