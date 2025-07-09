from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
import sys

CHROMEDRIVER_PATH = "C:/bin/chromedriver-win64/chromedriver.exe"
PROFILE_PATH = "C:/bin/whatsapp_profile"

def abrir_whatsapp_e_instagram():
    options = Options()
    options.add_argument(f"user-data-dir={PROFILE_PATH}")

    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        print(f"❌ Error iniciando ChromeDriver: {e}")
        sys.exit(1)

    try:
        driver.get("https://web.whatsapp.com/")
    except TimeoutException as e:
        print(f"⚠️ Timeout cargando WhatsApp Web: {e}")

    try:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get("https://www.instagram.com/accounts/login/")
    except Exception as e:
        print(f"⚠️ Error abriendo Instagram: {e}")

    print("WhatsApp Web e Instagram abiertos en dos pestañas.")
    input("Presiona ENTER para cerrar el navegador...")

    driver.quit()

if __name__ == "__main__":
    abrir_whatsapp_e_instagram()