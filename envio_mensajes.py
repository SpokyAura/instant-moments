import time
import random
import re
import pyperclip
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Importa el logger ya configurado (ajusta el nombre del módulo según tu proyecto)
from logger_config import logger

def anexar_fase(texto, fase_actual):
    try:
        texto = texto.strip()
        texto = re.sub(r"\s*\(Fase \d+\)$", "", texto)
        return f"{texto} (Fase {fase_actual})"
    except Exception as e:
        logger.warning(f"Error en anexar_fase: {e}", exc_info=True)
        return texto

def formatear_telefono(telefono):
    try:
        return ''.join(filter(str.isdigit, str(telefono)))
    except Exception as e:
        logger.warning(f"Error formateando teléfono '{telefono}': {e}", exc_info=True)
        return ""

def enviar_mensaje(driver, telefono, mensaje):
    try:
        telefono_formateado = formatear_telefono(telefono)
        if not telefono_formateado:
            logger.error("Teléfono inválido o vacío.")
            return False, "teléfono inválido"

        url = f"https://wa.me/{telefono_formateado}"
        driver.get(url)

        wait = WebDriverWait(driver, 15)

        try:
            error_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'no es válido')]"))
            )
            if error_element:
                logger.error(f"WhatsApp indica que el número {telefono_formateado} no es válido.")
                return False, "número no válido"
        except TimeoutException:
            pass

        btn_ir_al_chat = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="action-button"]/span'))
        )
        btn_ir_al_chat.click()
        time.sleep(2)

        btn_usar_wa = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="fallback_block"]/div/div/h4[2]/a/span'))
        )
        btn_usar_wa.click()
        time.sleep(3)

        wait.until(EC.presence_of_element_located((By.ID, "main")))

        caja_mensaje = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]/p'))
        )
        caja_mensaje.click()
        time.sleep(0.5)

        pyperclip.copy(mensaje)
        caja_mensaje.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        boton_enviar = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/button'))
        )
        boton_enviar.click()

        logger.info(f"Mensaje enviado por WhatsApp a {telefono_formateado}.")
        return True, "Mensaje enviado"

    except TimeoutException:
        logger.warning(f"Timeout esperando elementos en WhatsApp para {telefono}.", exc_info=True)
        return False, "timeout"
    except WebDriverException as e:
        logger.error(f"Error WebDriver al enviar mensaje a {telefono}: {e}", exc_info=True)
        return False, f"WebDriver error: {str(e)}"
    except Exception as e:
        logger.error(f"Error inesperado al enviar mensaje a {telefono}: {e}", exc_info=True)
        return False, f"otro error: {str(e)}"

def agregar_fase_participada(contacto, fase_actual):
    try:
        fases = contacto.get("Fases participadas", "").strip()
        fases_lista = [f.strip() for f in fases.split(",") if f.strip()]
        if str(fase_actual) not in fases_lista:
            fases_lista.append(str(fase_actual))
        return ", ".join(fases_lista)
    except Exception as e:
        logger.warning(f"Error en agregar_fase_participada: {e}", exc_info=True)
        return contacto.get("Fases participadas", "")

def enviar_mensajes_contactos(
    driver, worksheet, contactos, fase_actual, generar_mensaje_func, columnas_idx,
    seguimiento=None, proxima_accion=None, marcar_recordatorio=False
):
    logger.info(f"Iniciando envío con {len(contactos)} contactos desde {generar_mensaje_func.__name__}...")

    try:
        col_mensaje = columnas_idx["mensaje_enviado_wa"]
        col_fecha = columnas_idx["fecha_envio_wa"]
        col_hora = columnas_idx["hora_envio_wa"]
        col_interes = columnas_idx["interes"]
        col_prox = columnas_idx["proxima_accion"]
        col_fases = columnas_idx["fases_participadas"]
        col_respondio = columnas_idx["respondio"]
        col_entrada_gratis = columnas_idx["entrada_gratis"]
        col_correo_verificado = columnas_idx["correo_verificado"]
        col_comentarios = columnas_idx.get("comentarios")
        col_recordatorio = columnas_idx.get("recordatorio_confirmacion")
    except KeyError as e:
        logger.error(f"Falta la columna esperada en indices: {e}", exc_info=True)
        return

    for contacto in contactos:
        fila = contacto.get("fila")
        nombre = contacto.get("Nombre", "amig@")
        telefono = str(contacto.get("Teléfono", "")).strip()

        if not fila or not telefono:
            logger.info(f"Saltando contacto sin fila o teléfono: {nombre}")
            continue

        respondio = str(contacto.get("Respondió", "")).strip().lower() == "true"
        if not respondio:
            logger.info(f"{nombre} no ha respondido, saltando.")
            continue

        try:
            try:
                mensaje = generar_mensaje_func(
                    nombre,
                    contacto.get("Correo", ""),
                    contacto.get("Instagram", ""),
                    telefono
                )
            except TypeError:
                mensaje = generar_mensaje_func(contacto)
        except Exception as e:
            logger.warning(f"Error generando mensaje para {nombre}: {e}", exc_info=True)
            continue

        if not mensaje:
            logger.info(f"No se generó mensaje para {nombre}, saltando.")
            continue

        logger.info(f"Enviando mensaje a {nombre}...")
        exito, resultado = enviar_mensaje(driver, telefono, mensaje)

        ahora = datetime.now()
        try:
            if exito:
                worksheet.update_cell(fila, col_mensaje, anexar_fase(resultado, fase_actual))
                worksheet.update_cell(fila, col_fecha, ahora.strftime("%Y-%m-%d"))
                worksheet.update_cell(fila, col_hora, ahora.strftime("%H:%M:%S"))
                worksheet.update_cell(fila, col_interes, "Alto")

                nuevas_fases = agregar_fase_participada(contacto, fase_actual)
                worksheet.update_cell(fila, col_fases, nuevas_fases)

                respondio = str(contacto.get("Respondió", "")).strip().lower() == "true"
                entrada_gratis = str(contacto.get("Entrada Gratis", "")).strip().lower() == "true"
                confirmo_asistencia = str(contacto.get("Confirmó Asistencia", "")).strip().lower() == "sí"

                if seguimiento is None:
                    if respondio and entrada_gratis and not confirmo_asistencia:
                        seguimiento = "Ganador - Entrada Gratis"
                    elif respondio and not entrada_gratis:
                        seguimiento = "Participante sin pase"

                if proxima_accion is None:
                    if respondio and entrada_gratis and not confirmo_asistencia:
                        proxima_accion = "Mandar mensaje Recordatorio de confirmación"
                    elif respondio and not entrada_gratis:
                        proxima_accion = "Mandar mensaje"

                if generar_mensaje_func.__name__ == "mensaje_recordatorio_confirmacion":
                    proxima_accion = "Esperar confirmación"

                if seguimiento and col_comentarios:
                    worksheet.update_cell(fila, col_comentarios, anexar_fase(seguimiento, fase_actual))

                if proxima_accion and col_prox:
                    worksheet.update_cell(fila, col_prox, anexar_fase(proxima_accion, fase_actual))

                if generar_mensaje_func.__name__ == "mensaje_recordatorio_confirmacion" and col_recordatorio:
                    worksheet.update_cell(fila, col_recordatorio, "TRUE")

            else:
                worksheet.update_cell(fila, col_mensaje, f"Error: {resultado}")

        except Exception as e:
            logger.warning(f"Error actualizando hoja para {nombre}, fila {fila}: {e}", exc_info=True)

        pausa = random.randint(7, 16)
        logger.info(f"Pausando {pausa} segundos antes de continuar...")
        time.sleep(pausa)
