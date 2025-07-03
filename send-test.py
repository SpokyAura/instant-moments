from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

# La función enviar_mensaje que ya te di arriba
def enviar_mensaje(driver, telefono, mensaje):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    try:
        url = f"https://wa.me/{telefono}?text={mensaje}"
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
            pass  # No apareció el mensaje de error, continuar

        # Clic en "Ir al chat"
        btn_ir_al_chat = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="action-button"]/span'))
        )
        btn_ir_al_chat.click()

        # Clic en "Usar WhatsApp Web"
        btn_usar_wa_web = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="fallback_block"]/div/div/h4[2]/a/span'))
        )
        btn_usar_wa_web.click()

        # Esperar a que aparezca la caja de texto del chat
        input_box = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
        )

        input_box.send_keys("\n")  # Enviar el mensaje con Enter

        print("✅ Mensaje enviado por WhatsApp.")
        return True, None

    except TimeoutException:
        print("⚠️ Timeout esperando elementos en WhatsApp.")
        return False, "timeout"
    except Exception as e:
        print(f"⚠️ Error inesperado al enviar mensaje: {e}")
        return False, "otro error"


if __name__ == "__main__":
    # Ajusta la ruta de chromedriver y el profile si quieres mantener sesión
    service = Service("C:/bin/chromedriver-win64/chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/bin/whatsapp_profile")  # Para sesión guardada

    driver = webdriver.Chrome(service=service, options=options)

    telefono_ejemplo = "5215512345678"  # Cambia por un número real para probar (con código país)
    mensaje_ejemplo = "Hola, este es un mensaje de prueba desde Selenium!"

    print("Abriendo WhatsApp...")
    driver.get("https://web.whatsapp.com")
    print("Por favor, asegúrate de que WhatsApp Web esté cargado y sesión iniciada.")
    time.sleep(15)  # Espera para que escanees QR si hace falta y cargue sesión

    exito, razon = enviar_mensaje(driver, telefono_ejemplo, mensaje_ejemplo)

    print(f"Resultado del envío: {exito}, Razón: {razon}")

    input("Presiona Enter para cerrar el navegador...")
    driver.quit()