# instagram_tools/verificar_perfiles.py
"""Script orquestador para comprobar la existencia de perfiles de Instagram
   y registrar el nº de seguidores en la hoja *IG‑IM*.

   Se apoya en:
   • ig_profile_check.verificar_perfil_instagram → scraping Selenium
   • sheets_ig.py → conexión y escritura en Google Sheets

   La función pública `revisar_perfiles_instagram()` puede llamarse desde
   `main.py`, respetando el flag `ACTIVAR_REVISION_IG` en config.py.
"""
from __future__ import annotations

import random
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

from logger_config import logger
from config import CHROMEDRIVER_PATH, CHROME_PROFILE_PATH

from ig_utils.ig_profile_check import verificar_perfil_instagram
from ig_utils.sheets_ig import (
    conectar_sheets_ig,
    obtener_indices_columnas_ig,
    obtener_perfiles_instagram,
    actualizar_perfil_resultado,
)

# ---------------------------------------------------------------------------
#   Parámetros de scraping IG
# ---------------------------------------------------------------------------

MAX_PERFILES_POR_EJECUCION = 80          # ← para evitar bloqueos de IG
PAUSA_MIN = 4                            # segundos entre perfiles (min)
PAUSA_MAX = 12                           # segundos entre perfiles (max)


# ---------------------------------------------------------------------------
#   Helper: iniciar Selenium
# ---------------------------------------------------------------------------

def _iniciar_driver_ig() -> webdriver.Chrome | None:
    try:
        options = Options()
        options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
        options.add_argument("--lang=es-ES")
        options.add_argument("--disable-blink-features=AutomationControlled")
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("Driver IG iniciado correctamente.")
        return driver
    except WebDriverException as e:
        logger.error("No se pudo iniciar Selenium IG: %s", e, exc_info=True)
        return None


# ---------------------------------------------------------------------------
#   Función pública
# ---------------------------------------------------------------------------

def revisar_perfiles_instagram(limite_perfiles: int | None = None):
    """Verifica perfiles IG listados en la hoja *IG‑IM*.

    Args
    ----
    limite_perfiles: int | None
        Máximo de perfiles a revisar en esta ejecución. Si None, usa
        MAX_PERFILES_POR_EJECUCION.
    """
    limite = limite_perfiles or MAX_PERFILES_POR_EJECUCION

    # 1) Conectar a la hoja IG‑IM
    worksheet = conectar_sheets_ig()
    if worksheet is None:
        logger.warning("Abortando revisión IG: no se pudo abrir la hoja IG‑IM.")
        return

    cols_idx = obtener_indices_columnas_ig(worksheet)
    perfiles = obtener_perfiles_instagram(worksheet, cols_idx)

    if not perfiles:
        logger.info("No hay perfiles de Instagram para revisar.")
        return

    logger.info("Perfiles IG obtenidos: %s", len(perfiles))

    # 2) Iniciar driver una sola vez
    driver = _iniciar_driver_ig()
    if driver is None:
        return

    procesados = 0
    try:
        for perfil in perfiles:
            if procesados >= limite:
                logger.info("Se alcanzó el límite de %s perfiles. Finalizando.", limite)
                break

            fila = perfil["fila"]
            usuario = perfil["usuario"].lstrip("@")

            logger.info("[%s/%s] Revisando @%s (fila %s)…", procesados + 1, limite, usuario, fila)
            existe, seguidores = verificar_perfil_instagram(driver, usuario)
            actualizar_perfil_resultado(
                worksheet,
                fila=fila,
                col_check=cols_idx["check"],
                col_seguidores=cols_idx["seguidores"],
                existe=existe,
                seguidores=seguidores,
            )

            procesados += 1

            # Pausa aleatoria para imitar comportamiento humano y evitar rate‑limit
            pausa = random.uniform(PAUSA_MIN, PAUSA_MAX)
            logger.debug("Pausa de %.2f s", pausa)
            time.sleep(pausa)

    finally:
        logger.info("Cerrando driver IG…")
        driver.quit()
        logger.info("Revisión IG finalizada. %s perfiles procesados.", procesados)
