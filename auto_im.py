import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from config import (
    CREDENTIALS_FILE,
    SPREADSHEET_ID,
    HOJA_ACTIVA,
    FASE_ACTUAL,
    CHROMEDRIVER_PATH,
    CHROME_PROFILE_PATH,
)

from sheets_utils import conectar_sheets, obtener_todas_las_filas
from envio_mensajes import enviar_mensajes_contactos
from mensajes import (
    mensaje_convocatoria_inicial,
    mensaje_ganador_entrada,
    mensaje_cercano_a_ganador,
    mensaje_recordatorio_confirmacion,
    mensaje_integracion_futuras_fases,
)

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
    # Agregar número de fila para actualizaciones en Sheets (gspread no da fila explícita)
    for i, contacto in enumerate(contactos, start=2):
        contacto["fila"] = i

    print("🚀 Iniciando Selenium WebDriver...")
    driver = iniciar_driver()

    # Clasificar contactos si quieres, o filtrar los que cumplen ciertas condiciones
    # Por ejemplo, enviar convocatoria inicial solo a los que no han respondido:
    contactos_no_respondieron = [c for c in contactos if str(c.get("Respondió", "")).lower() != "true"]

    # Enviar mensaje convocatoria inicial a quienes no respondieron
    print(f"✉️ Enviando mensajes de convocatoria inicial a {len(contactos_no_respondieron)} contactos...")
    enviar_mensajes_contactos(driver, worksheet, contactos_no_respondieron, FASE_ACTUAL, mensaje_convocatoria_inicial)

    # Ejemplo: enviar mensaje a ganadores que no han confirmado (respondieron==true pero sin confirmar)
    contactos_ganadores_pendientes = [
        c for c in contactos
        if str(c.get("Respondió", "")).lower() == "true"
        and str(c.get("Entrada Gratis", "")).lower() == "true"
        and (c.get("Confirmó Asistencia", "") != "Sí")  # Ajusta esta lógica si tienes esa columna
    ]
    print(f"✉️ Enviando recordatorio a ganadores pendientes ({len(contactos_ganadores_pendientes)})...")
    enviar_mensajes_contactos(driver, worksheet, contactos_ganadores_pendientes, FASE_ACTUAL, mensaje_recordatorio_confirmacion)

    # También puedes enviar otros tipos de mensajes usando la función de envío general:
    # Por ejemplo, mensaje de integración a futuras fases a los que respondieron.
    contactos_respondieron = [c for c in contactos if str(c.get("Respondió", "")).lower() == "true"]
    print(f"✉️ Enviando mensajes de integración a {len(contactos_respondieron)} contactos que respondieron...")
    enviar_mensajes_contactos(driver, worksheet, contactos_respondieron, FASE_ACTUAL, mensaje_integracion_futuras_fases)

    print("✅ Finalizado envío de mensajes.")
    driver.quit()

if __name__ == "__main__":
    main()
