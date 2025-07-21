# ig_utils/ig_profile_check.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import logging

logger = logging.getLogger(__name__)

def verificar_perfil_instagram(driver, usuario):
    """
    Verifica si un perfil de Instagram existe y obtiene el número de seguidores.

    Args:
        driver (webdriver.Chrome): Instancia de Selenium WebDriver.
        usuario (str): Nombre de usuario de Instagram (sin '@').

    Returns:
        (bool, int): Tupla con existencia del perfil y número de seguidores (0 si no existe o error).
    """
    url = f"https://www.instagram.com/{usuario}/"
    logger.debug(f"Accediendo a URL: {url}")

    try:
        driver.get(url)

        # Espera hasta que el main header de perfil esté presente o timeout 10s
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section main div header"))
        )

    except TimeoutException:
        # Si tarda mucho, podría ser que la página no cargó o está bloqueada
        logger.warning(f"Timeout esperando carga del perfil @{usuario}. Verificando si existe.")
    except Exception as e:
        logger.error(f"Error al cargar la página de {usuario}: {e}")
        return False, 0

    pagina = driver.page_source.lower()

    # Texto que indica que el perfil no existe
    mensajes_no_disponible = [
        "esta página no está disponible."
    ]

    if any(msg in pagina for msg in mensajes_no_disponible):
        logger.info(f"Perfil @{usuario} no encontrado: mensaje de página no disponible detectado.")
        return False, 0

    # Intentar obtener el número de seguidores con XPath directo
    xpath_seguidores = '//section/main/div/header/section[3]/ul/li[2]/div/a/span/span/span'

    try:
        # Espera hasta 5 seg que aparezca el elemento del número de seguidores
        elemento = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath_seguidores))
        )
        seguidores_texto = elemento.text.strip()
        logger.debug(f"Texto de seguidores para @{usuario} (XPath directo): {seguidores_texto}")
    except TimeoutException:
        logger.warning(f"No se encontró el XPath directo para seguidores en @{usuario}, intentando búsqueda alternativa...")

        # Búsqueda alternativa: buscar el <li> con texto que contenga 'seguidores' (sin importar mayúsc/minúsc)
        try:
            ul_element = driver.find_element(By.XPATH, '//section/main/div/header/section[3]/ul')
            lis = ul_element.find_elements(By.TAG_NAME, 'li')
            seguidores_texto = None
            for li in lis:
                texto_li = li.text.lower()
                if 'seguidores' in texto_li:
                    # Buscar el número dentro del texto del li
                    seguidores_texto = _extraer_numero_de_texto(li.text)
                    if seguidores_texto:
                        logger.debug(f"Texto de seguidores para @{usuario} (búsqueda alternativa): {seguidores_texto}")
                        break
            if seguidores_texto is None:
                logger.warning(f"No se pudo extraer número de seguidores para @{usuario} con búsqueda alternativa.")
                seguidores_texto = "0"
        except Exception as e2:
            logger.error(f"Error buscando número de seguidores alternativo para @{usuario}: {e2}")
            seguidores_texto = "0"

    except Exception as e:
        logger.error(f"Error extrayendo seguidores para @{usuario}: {e}")
        seguidores_texto = "0"

    seguidores = _convertir_texto_seguidores_a_numero(seguidores_texto)
    return True, seguidores


def _extraer_numero_de_texto(texto):
    """
    Extrae la parte numérica del texto, por ejemplo de "1,234 seguidores" extrae "1,234".

    Args:
        texto (str): Texto completo.

    Returns:
        str | None: Número como string o None si no encontró nada.
    """
    import re
    m = re.search(r"([\d.,]+)", texto)
    if m:
        return m.group(1)
    return None


def _convertir_texto_seguidores_a_numero(texto):
    """
    Convierte texto de seguidores de Instagram (ej. "1,234", "1.2k", "75 mil", "2.3 millones") a entero.

    Args:
        texto (str): Texto que representa seguidores.

    Returns:
        int: Número entero de seguidores.
    """
    texto = texto.lower().replace(',', '').strip()

    try:
        if 'mil' in texto:
            numero = re.search(r'\d+(?:[\.,]\d+)?', texto)
            if numero:
                return int(float(numero.group(0).replace(',', '.')) * 1_000)
        elif 'millones' in texto or 'millón' in texto:
            numero = re.search(r'\d+(?:[\.,]\d+)?', texto)
            if numero:
                return int(float(numero.group(0).replace(',', '.')) * 1_000_000)
        elif 'k' in texto:
            return int(float(texto.replace('k', '').replace(',', '.')) * 1_000)
        elif 'm' in texto:
            return int(float(texto.replace('m', '').replace(',', '.')) * 1_000_000)
        else:
            return int(re.sub(r'[^\d]', '', texto))
    except Exception as e:
        logger.error(f"Error convirtiendo texto '{texto}' a número: {e}")
        return 0
