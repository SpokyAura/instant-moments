from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

CHROMEDRIVER_PATH = "C:/bin/chromedriver-win64/chromedriver.exe"
PROFILE_PATH = "C:/bin/whatsapp_profile"

def abrir_whatsapp_e_instagram():
    options = Options()
    options.add_argument(f"user-data-dir={PROFILE_PATH}")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # Abrir WhatsApp Web
    driver.get("https://web.whatsapp.com/")

    # Abrir nueva pestaña para Instagram
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://www.instagram.com/accounts/login/")

    print("WhatsApp Web e Instagram abiertos en dos pestañas.")
    input("Presiona ENTER para cerrar el navegador...")

    driver.quit()

if __name__ == "__main__":
    abrir_whatsapp_e_instagram()