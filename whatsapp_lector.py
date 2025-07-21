import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import CHROMEDRIVER_PATH, CHROME_PROFILE_PATH
from logger_config import logger

def obtener_mensajes_whatsapp_desde_selenium(n_max=None):
    """
    Abre WhatsApp Web, detecta chats con mensajes no leídos y extrae teléfonos.
    Devuelve una lista de tuplas: (telefono, orden_de_respuesta, preview)
    """
    options = Options()
    options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 30)
    mensajes = []

    try:
        driver.get("https://web.whatsapp.com/")
        wait.until(EC.presence_of_element_located((By.ID, "pane-side")))
        logger.info("✅ WhatsApp Web cargado correctamente.")

        chats_leidos = set()
        scroll_intentos = 0

        while True:
            time.sleep(2)
            chats = driver.find_elements(By.XPATH, "//div[@id='pane-side']//div[contains(@aria-label, 'Chat')]")
            nuevos = 0

            for chat in chats:
                try:
                    if chat in chats_leidos:
                        continue

                    # Verifica si tiene contador de mensajes no leídos
                    badge = chat.find_elements(By.XPATH, ".//span[@data-icon='unread-count']")
                    if not badge:
                        chats_leidos.add(chat)
                        continue

                    chat.click()
                    time.sleep(2)

                    # Obtener número de teléfono del encabezado del chat
                    header = wait.until(EC.presence_of_element_located((By.XPATH, "//header//span[@dir='auto']")))
                    telefono = header.text

                    # Preview del último mensaje
                    bubbles = driver.find_elements(By.XPATH, "//div[@data-testid='msg-container']")
                    ultimo = bubbles[-1].text if bubbles else ""

                    mensajes.append((telefono, len(mensajes) + 1, ultimo))
                    logger.info(f"📥 {telefono}: {ultimo}")

                    chats_leidos.add(chat)
                    if n_max and len(mensajes) >= n_max:
                        raise StopIteration
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando chat: {e}")
                    continue

            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 500", driver.find_element(By.ID, "pane-side"))
            scroll_intentos += 1
            if scroll_intentos > 10 or (n_max and len(mensajes) >= n_max):
                break

    except StopIteration:
        logger.info("✅ Se alcanzó el límite solicitado.")
    except TimeoutException:
        logger.error("❌ Error cargando WhatsApp Web.")
    finally:
        driver.quit()

    return mensajes

if __name__ == "__main__":
    resultado = obtener_mensajes_whatsapp_desde_selenium()
    for tel, orden, texto in resultado:
        logger.info(f"#{orden}: {tel} => {texto}")