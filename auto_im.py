import time, re, random, pyperclip
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import quote

# --- Configuración Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_FILE = r'C:\bin\instant-moments\pivotal-mode-464204-t6-673f1678ee71.json'
SPREADSHEET_ID = "15kXq5wrYb9gJ0afeq_l82Fhj956gQryS1mB8OmzT5hI"

# --- Conectar a Google Sheets ---
def conectar_sheets():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet

# --- Limpiar texto ---
def limpiar_texto(texto):
    return re.sub(r'[^\w\s@.\-_]', '', texto).strip()

# --- Obtener contactos pendientes ---
def obtener_contactos_pendientes(sheet):
    worksheet = sheet.sheet1
    datos = worksheet.get_all_records()
    encabezados = worksheet.row_values(1)
    print(f"Encabezados detectados: {encabezados}")

    pendientes_whatsapp = []
    pendientes_instagram = []
    pendientes_seguimiento = []

    for idx, fila in enumerate(datos):
        fila_num = idx + 2  # porque la fila 1 son encabezados

        nombre = fila.get("Nombre", "")
        telefono = str(fila.get("Teléfono", "")).strip()
        instagram = fila.get("Instagram", "").strip()
        responded = str(fila.get("Respondió", "")).lower() == "true"
        mensaje_wa = fila.get("Mensaje enviado WA", "").strip()
        mensaje_ig = fila.get("Mensaje enviado IG", "").strip()
        seguimiento = fila.get("Comentarios / Seguimiento", "").strip()
        interes = fila.get("Interés", "").strip()

        # --- Actualizar interés a 'Alto' si corresponde ---
        if responded and interes.lower() != "alto":
            worksheet.update_cell(fila_num, 11, "Alto")  # Columna K
            print(f"⬆️ Interés actualizado a 'Alto' para {nombre}")

        # --- Clasificaciones ---
        if not mensaje_wa:
            pendientes_whatsapp.append({**fila, "fila": fila_num})

        if not mensaje_ig and instagram:
            pendientes_instagram.append({**fila, "fila": fila_num})

        if responded and not seguimiento:
            pendientes_seguimiento.append({**fila, "fila": fila_num})

    print(f"\n✅ Contactos pendientes:")
    print(f"📱 WhatsApp: {len(pendientes_whatsapp)}")
    for c in pendientes_whatsapp[:3]:
        print(f"   - {c.get('Nombre')}")

    print(f"📸 Instagram: {len(pendientes_instagram)}")
    for c in pendientes_instagram[:3]:
        print(f"   - {c.get('Nombre')}")

    print(f"🔁 Seguimiento: {len(pendientes_seguimiento)}")
    for c in pendientes_seguimiento[:3]:
        print(f"   - {c.get('Nombre')}")

    return worksheet, pendientes_whatsapp, pendientes_instagram, pendientes_seguimiento

def formatear_telefono(raw_tel):
    # Limpia espacios y guiones
    tel = raw_tel.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    # Si empieza con '+', quitarlo
    if tel.startswith("+"):
        tel = tel[1:]

    # Si empieza con '0' (número nacional), reemplazarlo por código México '52'
    if tel.startswith("0"):
        tel = "52" + tel[1:]

    # Si empieza con '52' o cualquier otro código país, lo dejamos así

    # Filtrar solo dígitos para evitar caracteres raros
    tel = ''.join(filter(str.isdigit, tel))

    return tel

# --- Crear mensaje personalizado ---
def crear_mensaje(contacto):
    nombre = contacto.get("Nombre", "Amig@")
    correo = contacto.get("Correo", "")
    instagram = contacto.get("Instagram", "")
    telefono = contacto.get("Teléfono", "")
    zona = contacto.get("Zona / Segmento", "").lower()
    idioma = "English" if zona == "extranjero" else "Español"

    if idioma == "English":
        mensaje = f"""Hello {nombre}, I hope you're doing great!

Thanks for being part of *Instant Moments*, in collaboration with *Cine Tonalá*.

🎁 The *first 30 people to reply to this message will get a free movie ticket* valid from July 3 to 31.

Check the available screenings here 👉 https://www.cinetonala.mx/

🎉 Everyone who participated in the project will also receive:

*2-for-1 on cocktails and drinks.*  
Just show your printed photo as many times as you want until Dec. 2025

Stay tuned for new experiences:  
📸 https://www.instagram.com/yoali.spindola/
"""
    else:
        mensaje = f"""Hola {nombre}, ¡espero que estés muy bien!

¡Gracias por participar en *Instant Moments*, en alianza con *Cine Tonalá*!

🎁 Si eres una de *las primeras 30 personas en responder este mensaje tendrás una entrada gratis al cine*, válida del 3 al 31 de julio.

Consulta las funciones disponibles aquí 👉 https://www.cinetonala.mx/

🎉 Además, todos los que participaron en este proyecto obtendrán:

*2x1 en coctelería y bebidas.*  
Solo presenta tu foto las veces que quieras hasta Dic. 2025

Sígueme para estar al tanto de las dinámicas:  
📸 https://www.instagram.com/yoali.spindola/
"""
    return mensaje

# --- Iniciar WhatsApp Web ---
def iniciar_whatsapp():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/bin/whatsapp_profile")
    service = Service("C:/bin/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://web.whatsapp.com")
    print("Esperando que WhatsApp Web cargue la sesión...")
    time.sleep(13)
    return driver

# --- Función para abrir Instagram en nueva pestaña ---
def abrir_instagram(driver):
    driver.execute_script("window.open('https://www.instagram.com/', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    print("Abriendo Instagram...")
    time.sleep(5)

# --- Enviar mensaje WhatsApp ---
def enviar_mensaje(driver, telefono, mensaje):
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

        # Usar el xpath correcto para el cuadro de mensaje
        caja_mensaje = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]/p'))
        )
        caja_mensaje.click()
        time.sleep(0.5)

        # Pegar el mensaje
        pyperclip.copy(mensaje)
        caja_mensaje.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # Clic en el botón de enviar
        boton_enviar = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/button'))
        )
        boton_enviar.click()

        print("✅ Mensaje enviado por WhatsApp.")
        return True, "Mensaje Inicial"

    except TimeoutException:
        print("⚠️ Timeout esperando elementos en WhatsApp.")
        return False, "timeout"
    except Exception as e:
        print(f"⚠️ Error inesperado al enviar mensaje: {e}")
        return False, f"otro error: {str(e)}"

# --- Función para enviar mensaje por Instagram ---
def enviar_mensaje_instagram(driver, instagram_user, mensaje):
    url = f"https://www.instagram.com/direct/new/"
    driver.get(url)

    try:
        # Espera que cargue el input para buscar usuario
        buscar_input_xpath = '//input[@name="queryBox"]'
        for _ in range(30):
            try:
                input_buscar = driver.find_element(By.XPATH, buscar_input_xpath)
                break
            except:
                time.sleep(1)
        else:
            print(f"❌ No se encontró el buscador de usuarios en Instagram")
            return False

        # Escribe el nombre de usuario
        input_buscar.clear()
        input_buscar.send_keys(instagram_user)
        time.sleep(3)  # espera resultados

        # Selecciona el usuario (primer resultado)
        primer_usuario_xpath = '//div[@role="dialog"]//div[contains(@class,"_aacl")][1]'
        driver.find_element(By.XPATH, primer_usuario_xpath).click()
        time.sleep(1)

        # Click en botón siguiente
        boton_siguiente_xpath = '//div[@role="dialog"]//button[text()="Siguiente"]'
        driver.find_element(By.XPATH, boton_siguiente_xpath).click()
        time.sleep(3)

        # Espera la caja de mensaje (contenteditable)
        caja_mensaje_xpath = '//div[@contenteditable="true"][@role="textbox"]'
        for _ in range(30):
            try:
                caja = driver.find_element(By.XPATH, caja_mensaje_xpath)
                break
            except:
                time.sleep(1)
        else:
            print(f"❌ No se encontró la caja de mensaje en Instagram")
            return False

        # Copia y pega el mensaje
        pyperclip.copy(mensaje)
        caja.click()
        caja.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)
        caja.send_keys(Keys.ENTER)

        print(f"✅ Mensaje enviado a Instagram: {instagram_user}")
        return True

    except Exception as e:
        print(f"❌ Error enviando mensaje a Instagram a {instagram_user}: {e}")
        return False

# --- Función para actualizar el estado en Google Sheets Whatsapp---
def marcar_envio_whatsapp(worksheet, fila, exito=True, razon="Mensaje Inicial"):
    col_mensaje = 6  # Columna "Mensaje enviado WA"
    col_fecha = 7    # Columna "Fecha de envío WA"
    col_hora = 8     # Columna "Hora de envío WA"

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    if exito:
        worksheet.update_cell(fila, col_mensaje, "Mensaje Inicial")
        worksheet.update_cell(fila, col_fecha, fecha)
        worksheet.update_cell(fila, col_hora, hora)
    else:
        worksheet.update_cell(fila, col_mensaje, razon or "No fue posible enviar")

# --- Función para actualizar el estado en Google Sheets Instagram---
def marcar_envio_instagram(worksheet, fila, exito=True, razon="Mensaje Inicial"):
    col_mensaje = 9   # Columna "Mensaje enviado IG"
    col_fecha = 10    # Columna "Fecha de envío IG"
    col_hora = 11     # Columna "Hora de envío IG"

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    if exito:
        worksheet.update_cell(fila, col_mensaje, razon)
        worksheet.update_cell(fila, col_fecha, fecha)
        worksheet.update_cell(fila, col_hora, hora)
    else:
        worksheet.update_cell(fila, col_mensaje, razon)

# --- Enviar mensajes de seguimiento WhatsApp ---
def enviar_mensajes_seguimiento(driver, worksheet, pendientes_seguimiento, fase_actual):
    for contacto in pendientes_seguimiento:
        fila = contacto["fila"]
        nombre = contacto.get("Nombre", "amig@")
        telefono = str(contacto.get("Teléfono", "")).strip().replace(" ", "").replace("-", "")
        entrada_gratis = str(contacto.get("Entrada Gratis", "")).lower() == "true"

        if telefono.startswith("0"):
            telefono = "+52" + telefono[1:]
        elif not telefono.startswith("+"):
            telefono = "+52" + telefono

        # Validar número
        if not telefono or not telefono.replace("+", "").isdigit() or len(telefono) < 10:
            print(f"❌ Teléfono inválido en seguimiento: {telefono} ({nombre})")
            worksheet.update_cell(fila, 6, "Teléfono inválido")  # Columna F - Mensaje enviado WA
            continue

        # Crear mensaje personalizado
        if entrada_gratis:
            mensaje = f"""🎉 ¡Hola {nombre}!

Gracias por participar en *Instant Moments*. 🎞️

🎁 ¡Felicidades! Fuiste de los primeros en responder y ganaste una *entrada gratis* para Cine Tonalá (válida del 2 al 16 de julio).

🎬 Consulta la cartelera 👉 https://www.cinetonala.mx/

Si tienes intención de asistir, por favor confirma tus datos para enviarte el pase:
📌 Nombre: {nombre}
📌 Correo:
📌 Instagram:
📌 Teléfono:

👉 *Confirma tu correo*, ya que Cine Tonalá lo usa para enviar los pases.

¡Gracias por ser parte! 🙌"""
            tipo_mensaje = "Ganador - Entrada Gratis"
        else:
            mensaje = f"""👋 ¡Hola {nombre}!

Gracias por responder a *Instant Moments* 🎞️

Esta vez no fuiste de los primeros 12 en responder 😢, pero tu participación sigue siendo muy valiosa.

🎁 La prioridad para los próximos beneficios es aleatoria, ¡pero quienes han respondido antes tienen más oportunidades!

Sigue al pendiente y sígueme en IG:
📸 https://www.instagram.com/yoali.spindola/

¡Gracias por participar y por tu energía! ✨"""
            tipo_mensaje = "Participante sin pase"

        # Enviar mensaje por WhatsApp
        exito, razon = enviar_mensaje(driver, telefono, mensaje)

        if exito:
            # Marcar columnas
            worksheet.update_cell(fila, 6, tipo_mensaje)      # "Mensaje enviado WA"
            worksheet.update_cell(fila, 7, datetime.now().strftime("%Y-%m-%d"))  # "Fecha de envío"
            worksheet.update_cell(fila, 8, datetime.now().strftime("%H:%M:%S"))  # "Hora de envío"
            worksheet.update_cell(fila, 17, tipo_mensaje)     # "Comentarios / Seguimiento"
            fases_anteriores = str(contacto.get("Fases participadas", "")).strip()
            nuevas_fases = f"{fases_anteriores}, {fase_actual}" if fases_anteriores else str(fase_actual)
            worksheet.update_cell(fila, 19, nuevas_fases)     # "Fases participadas" (columna S = 19)
            print(f"✅ Seguimiento enviado a {nombre}")
        else:
            worksheet.update_cell(fila, 6, razon or "Error seguimiento")
            print(f"⚠️ Error enviando seguimiento a {nombre}: {razon}")

        # Espera entre mensajes
        delay = random.randint(10, 32)
        print(f"⏳ Esperando {delay} segundos antes del siguiente seguimiento...")
        time.sleep(delay)

# --- Función principal ---
def main():
    ENVIAR_WHATSAPP = True         # Envío de mensajes iniciales por WhatsApp
    ENVIAR_INSTAGRAM = False       # Envío por Instagram
    ENVIAR_SEGUIMIENTO = True      # Mensajes de seguimiento por WhatsApp
    FASE_ACTUAL = 1                # Número de fase actual

    sheet = conectar_sheets()
    worksheet, pendientes_whatsapp, pendientes_instagram, pendientes_seguimiento = obtener_contactos_pendientes(sheet)

    if (ENVIAR_WHATSAPP and not pendientes_whatsapp) and \
       (ENVIAR_INSTAGRAM and not pendientes_instagram) and \
       (ENVIAR_SEGUIMIENTO and not pendientes_seguimiento):
        print("✅ No hay contactos pendientes para enviar.")
        return

    driver = iniciar_whatsapp()

    # --- Enviar mensajes iniciales por WhatsApp ---
    if ENVIAR_WHATSAPP and pendientes_whatsapp:
        for contacto in pendientes_whatsapp:
            try:
                telefono = str(contacto.get("Teléfono", "")).replace(" ", "").replace("-", "")
                if telefono.startswith("0"):
                    telefono = "+52" + telefono[1:]
                elif not telefono.startswith("+"):
                    telefono = "+52" + telefono

                if not telefono or not telefono.replace("+", "").isdigit() or len(telefono) < 10:
                    print(f"❌ Teléfono inválido: {telefono} ({contacto.get('Nombre')})")
                    marcar_envio_whatsapp(worksheet, contacto["fila"], exito=False, razon="Teléfono inválido")
                    continue

                mensaje = crear_mensaje(contacto)
                exito, razon = enviar_mensaje(driver, telefono, mensaje)
                marcar_envio_whatsapp(worksheet, contacto["fila"], exito, razon)

            except Exception as e:
                print(f"⚠️ Error WA con {contacto.get('Nombre')}: {e}")
                marcar_envio_whatsapp(worksheet, contacto["fila"], exito=False, razon="Error inesperado")

            delay = random.randint(2, 5)
            print(f"⏳ Esperando {delay} segundos antes del siguiente mensaje WA...")
            time.sleep(delay)

    # --- Enviar mensajes por Instagram ---
    if ENVIAR_INSTAGRAM and pendientes_instagram:
        for contacto in pendientes_instagram:
            try:
                mensaje = crear_mensaje(contacto)
                exito = enviar_mensaje_instagram(driver, contacto, mensaje)
                marcar_envio_instagram(worksheet, contacto["fila"], exito)
            except Exception as e:
                print(f"⚠️ Error IG con {contacto.get('Nombre')}: {e}")
                marcar_envio_instagram(worksheet, contacto["fila"], exito=False, razon="Error inesperado")

            delay = random.randint(2, 5)
            print(f"⏳ Esperando {delay} segundos antes del siguiente mensaje IG...")
            time.sleep(delay)

    # --- Enviar mensajes de seguimiento ---
    if ENVIAR_SEGUIMIENTO and pendientes_seguimiento:
        enviar_mensajes_seguimiento(driver, worksheet, pendientes_seguimiento, FASE_ACTUAL)

    input("🟢 Proceso terminado. Presiona Enter para cerrar el navegador...")
    driver.quit()

# --- Ejecutar ---
if __name__ == "__main__":
    main()