import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from config import (
    FASE_ACTUAL,
    CHROMEDRIVER_PATH,
    CHROME_PROFILE_PATH,
    ENVIAR_MENSAJES_INICIALES,
    ENVIAR_RECORDATORIOS_CONFIRMACION,
    ENVIAR_MENSAJES_INTEGRACION,
    ENVIAR_MENSAJES_RESULTADOS,
    REVISION_RESPUESTAS,
    LOG_DATOS
)

# Inicializa el archivo de log solo si está activado el flag
inicializar_log()

from sheets_utils import conectar_sheets, obtener_todas_las_filas, obtener_indices_columnas, actualizar_interes_alto_batch
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

def iniciar_driver():
    """Inicia el driver de Chrome con el perfil y opciones necesarias."""
    options = Options()
    options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def main():
    print("🔄 Iniciando conexión con Google Sheets...")
    worksheet = conectar_sheets()

    print("📋 Obteniendo contactos desde la hoja...")
    contactos = obtener_todas_las_filas(worksheet)
    for i, contacto in enumerate(contactos, start=2):
        contacto["fila"] = i

    print("📊 Obteniendo índices de columnas...")
    columnas_idx = obtener_indices_columnas(worksheet)

    print("Actualizando interés a Alto para contactos con Respondió o Entrada Gratis...")
    actualizar_interes_alto_batch(worksheet, contactos, columnas_idx)

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

    print("🔎 Contactos sin pase detectados:")
    for c in contactos_resultados_sin_pase:
        print(f"- {c.get('Nombre')} | Respondió: {c.get('Respondió')} | Entrada Gratis: {c.get('Entrada Gratis')} | Comentarios: {c.get('Comentarios / Seguimiento')}")

    print("🔎 Contactos con pase detectados:")
    for c in contactos_resultados_con_pase:
        print(f"- {c.get('Nombre')} | Respondió: {c.get('Respondió')} | Entrada Gratis: {c.get('Entrada Gratis')} | Comentarios: {c.get('Comentarios / Seguimiento')}")

    print("🚀 Iniciando Selenium WebDriver...")
    driver = iniciar_driver()

    contactos_no_respondieron = [
        c for c in contactos if str(c.get("Respondió", "")).lower() != "true"
    ]
    contactos_ganadores_pendientes = [
        c for c in contactos
        if str(c.get("Respondió", "")).lower() == "true"
        and str(c.get("Entrada Gratis", "")).lower() == "true"
        and str(c.get("Confirmó Asistencia", "")).lower() != "sí"
    ]
    contactos_respondieron = [
        c for c in contactos if str(c.get("Respondió", "")).lower() == "true"
    ]

    if ENVIAR_MENSAJES_INICIALES:
        print(f"✉️ Enviando mensajes de convocatoria inicial a {len(contactos_no_respondieron)} contactos...")
        enviar_mensajes_contactos(driver, worksheet, contactos_no_respondieron, FASE_ACTUAL, mensaje_convocatoria_inicial, columnas_idx)
    else:
        print("✉️ Saltando envío de mensajes de convocatoria inicial.")

    if ENVIAR_MENSAJES_RESULTADOS:
        print(f"✉️ Enviando mensaje a participantes sin pase ({len(contactos_resultados_sin_pase)})...")
        enviar_mensajes_contactos(driver, worksheet, contactos_resultados_sin_pase, FASE_ACTUAL, mensaje_cercano_a_ganador, columnas_idx, seguimiento="Participante sin pase")

        print(f"✉️ Enviando mensaje a ganadores sin seguimiento ({len(contactos_resultados_con_pase)})...")
        enviar_mensajes_contactos(driver, worksheet, contactos_resultados_con_pase, FASE_ACTUAL, mensaje_ganador_entrada, columnas_idx, seguimiento="Ganador - Entrada Gratis", proxima_accion="Mandar mensaje Recordatorio de confirmación")
    else:
        print("✉️ Saltando envío de mensajes de resultados.")

    if ENVIAR_RECORDATORIOS_CONFIRMACION:
        print(f"✉️ Enviando recordatorio a ganadores pendientes ({len(contactos_ganadores_pendientes)})...")
        enviar_mensajes_contactos(driver, worksheet, contactos_ganadores_pendientes, FASE_ACTUAL, mensaje_recordatorio_confirmacion,
            columnas_idx,
            marcar_recordatorio=True
        )
    else:
        print("✉️ Saltando envío de recordatorios de confirmación.")

    if REVISION_RESPUESTAS:
        print("🔍 Revisando respuestas recibidas y asignando entradas gratis...")
        ganadores = revisar_respuestas(hoja_datos, COLUMNAS)
        print(f"🏆 Ganadores asignados: {len(ganadores)} contactos.")
    else:
        print("🔍 Saltando revisión automática de respuestas.")

    if ENVIAR_MENSAJES_INTEGRACION:
        print(f"✉️ Enviando mensajes de integración a {len(contactos_respondieron)} contactos que respondieron...")
        enviar_mensajes_contactos(driver, worksheet, contactos_respondieron, FASE_ACTUAL, mensaje_integracion_futuras_fases, columnas_idx)
    else:
        print("✉️ Saltando envío de mensajes de integración.")

    print("✅ Finalizado envío de mensajes.")
    driver.quit()

    if LOG_DATOS:
        registrar_estadistica(
            fase=FASE_ACTUAL,
            mensajes_enviados=len(contactos_enviados),
            respuestas_recibidas=len(contactos_respondieron),
            entradas_gratis=sum(1 for c in contactos_enviados if c.get("Entrada Gratis") == True),
            comentarios=f"Resumen fase {FASE_ACTUAL}"
        )
        print(f"📊 Estadísticas de fase {FASE_ACTUAL} registradas en log_fases.csv")

if __name__ == "__main__":
    main()