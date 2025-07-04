import time
import pyperclip
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import COLUMNAS

def formatear_telefono(telefono):
    """Devuelve el número de teléfono solo con dígitos, sin espacios, guiones ni signos."""
    return ''.join(filter(str.isdigit, str(telefono)))

def enviar_mensaje(driver, telefono, mensaje):
    """Envía un mensaje único a un número de WhatsApp usando Selenium."""
    try:
        telefono_formateado = formatear_telefono(telefono)
        url = f"https://wa.me/{telefono_formateado}"
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)

        # Verificar si el número no es válido
        try:
            error_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'no es válido')]"))
            )
            if error_element:
                print("❌ WhatsApp indica que el número no es válido.")
                return False, "número no válido"
        except TimeoutException:
            pass

        # Ir al chat
        btn_ir_al_chat = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="action-button"]/span'))
        )
        btn_ir_al_chat.click()
        time.sleep(2)

        # Usar WhatsApp Web
        btn_usar_wa = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="fallback_block"]/div/div/h4[2]/a/span'))
        )
        btn_usar_wa.click()
        time.sleep(3)

        # Esperar que cargue el área de chat
        wait.until(EC.presence_of_element_located((By.ID, "main")))

        # Escribir el mensaje
        caja_mensaje = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]/p'))
        )
        caja_mensaje.click()
        time.sleep(0.5)
        pyperclip.copy(mensaje)
        caja_mensaje.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # Enviar mensaje
        boton_enviar = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/button'))
        )
        boton_enviar.click()

        print("✅ Mensaje enviado por WhatsApp.")
        return True, "Mensaje enviado"

    except TimeoutException:
        print("⚠️ Timeout esperando elementos en WhatsApp.")
        return False, "timeout"
    except Exception as e:
        print(f"⚠️ Error inesperado al enviar mensaje: {e}")
        return False, f"otro error: {str(e)}"


def agregar_fase_participada(contacto, fase_actual):
    """
    Añade la fase actual al campo 'Fases participadas' si no está ya.
    """
    fases = contacto.get(COLUMNAS["fases_participadas"], "").strip()
    fases_lista = [f.strip() for f in fases.split(",") if f.strip()]
    if str(fase_actual) not in fases_lista:
        fases_lista.append(str(fase_actual))
    return ", ".join(fases_lista)


def enviar_mensajes_contactos(driver, worksheet, contactos, fase_actual, generar_mensaje_func):
    """
    Envía mensajes a una lista de contactos y actualiza la hoja de Google Sheets.
    
    Params:
      - driver: Selenium WebDriver
      - worksheet: objeto worksheet de gspread
      - contactos: lista de diccionarios con datos
      - fase_actual: número de fase actual (int o str)
      - generar_mensaje_func: función que recibe un contacto y devuelve el texto personalizado
    """
    # Obtener índices de columnas para actualizar
    col_mensaje = COLUMNAS["mensaje_wa_idx"]
    col_fecha = COLUMNAS["fecha_wa_idx"]
    col_hora = COLUMNAS["hora_wa_idx"]
    col_interes = COLUMNAS["interes_idx"]
    col_prox = COLUMNAS["proxima_accion_idx"]
    col_fases = COLUMNAS["fases_participadas_idx"]
    col_respondio = COLUMNAS["respondio_idx"]
    col_entrada_gratis = COLUMNAS["entrada_gratis_idx"]

    for contacto in contactos:
        fila = contacto.get("fila")
        nombre = contacto.get(COLUMNAS["nombre"], "amig@")
        telefono = contacto.get(COLUMNAS["telefono"], "").strip()
        if not fila or not telefono:
            print(f"⏭️ Saltando contacto sin fila o teléfono: {nombre}")
            continue  # Ignorar filas sin datos importantes

        respondio = str(contacto.get(COLUMNAS["respondio"], "")).strip().lower() == "true"
        if not respondio:
            print(f"⏭️ {nombre} no ha respondido, saltando.")
            continue

        mensaje = generar_mensaje_func(contacto)
        if not mensaje:
            print(f"⏭️ No se generó mensaje para {nombre}, saltando.")
            continue

        print(f"📨 Enviando mensaje a {nombre}...")
        exito, resultado = enviar_mensaje(driver, telefono, mensaje)

        ahora = datetime.now()
        if exito:
            worksheet.update_cell(fila, col_mensaje, resultado)
            worksheet.update_cell(fila, col_fecha, ahora.strftime("%Y-%m-%d"))
            worksheet.update_cell(fila, col_hora, ahora.strftime("%H:%M:%S"))
            worksheet.update_cell(fila, col_interes, "Alto")

            nuevas_fases = agregar_fase_participada(contacto, fase_actual)
            worksheet.update_cell(fila, col_fases, nuevas_fases)

            # Puedes actualizar la próxima acción aquí si quieres
            # worksheet.update_cell(fila, col_prox, "Acción siguiente")

        else:
            worksheet.update_cell(fila, col_mensaje, f"Error: {resultado}")

        time.sleep(2)  # Pausa para evitar bloqueos o spam