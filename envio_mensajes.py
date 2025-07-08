import time, random
import pyperclip
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def formatear_telefono(telefono):
    return ''.join(filter(str.isdigit, str(telefono)))

def enviar_mensaje(driver, telefono, mensaje):
    try:
        telefono_formateado = formatear_telefono(telefono)
        url = f"https://wa.me/{telefono_formateado}"
        driver.get(url)

        wait = WebDriverWait(driver, 15)

        # Comprobar número no válido
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

        wait.until(EC.presence_of_element_located((By.ID, "main")))

        # Escribir mensaje
        caja_mensaje = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]/p'))
        )
        caja_mensaje.click()
        time.sleep(0.5)
        pyperclip.copy(mensaje)
        caja_mensaje.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # Enviar
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
    fases = contacto.get("Fases participadas", "").strip()
    fases_lista = [f.strip() for f in fases.split(",") if f.strip()]
    if str(fase_actual) not in fases_lista:
        fases_lista.append(str(fase_actual))
    return ", ".join(fases_lista)

def enviar_mensajes_contactos(
    driver, worksheet, contactos, fase_actual, generar_mensaje_func, columnas_idx,
    seguimiento=None, proxima_accion=None, marcar_recordatorio=False
):
    print(f"📬 Iniciando envío con {len(contactos)} contactos desde {generar_mensaje_func.__name__}...")

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

    for contacto in contactos:
        fila = contacto.get("fila")
        nombre = contacto.get("Nombre", "amig@")
        telefono = str(contacto.get("Teléfono", "")).strip()

        if not fila or not telefono:
            print(f"⏭️ Saltando contacto sin fila o teléfono: {nombre}")
            continue

        respondio = str(contacto.get("Respondió", "")).strip().lower() == "true"
        if not respondio:
            print(f"⏭️ {nombre} no ha respondido, saltando.")
            continue

        try:
            mensaje = generar_mensaje_func(
                nombre,
                contacto.get("Correo", ""),
                contacto.get("Instagram", ""),
                telefono
            )
        except TypeError:
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

            # Variables de estado
            respondio = str(contacto.get("Respondió", "")).strip().lower() == "true"
            entrada_gratis = str(contacto.get("Entrada Gratis", "")).strip().lower() == "true"
            confirmo_asistencia = str(contacto.get("Confirmó Asistencia", "")).strip().lower() == "sí"

            # Si no vienen desde auto_im.py, determinar automáticamente
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

            # Si el mensaje es recordatorio de confirmación, forzar esta próxima acción
            if generar_mensaje_func.__name__ == "mensaje_recordatorio_confirmacion":
                proxima_accion = "Esperar confirmación"

            if seguimiento and col_comentarios:
                worksheet.update_cell(fila, col_comentarios, seguimiento)

            if proxima_accion and col_prox:
                worksheet.update_cell(fila, col_prox, proxima_accion)

            # Marcar casilla de "Recordatorio Enviado" solo si estamos enviando recordatorios
            if generar_mensaje_func.__name__ == "mensaje_recordatorio_confirmacion" and col_recordatorio:
                worksheet.update_cell(fila, col_recordatorio, "TRUE")
        else:
            worksheet.update_cell(fila, col_mensaje, f"Error: {resultado}")

        pausa = random.randint(7, 16)
        print(f"⏸️ Pausando {pausa} segundos antes de continuar...")
        time.sleep(pausa)