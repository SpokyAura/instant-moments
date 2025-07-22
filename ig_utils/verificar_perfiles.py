"""Script orquestador para comprobar la existencia de perfiles de Instagram
   y registrar el nº de seguidores en la hoja *IG‑IM*.

   Se apoya en:
   • ig_profile_check.verificar_perfil_instagram → scraping Selenium
   • sheets_ig.py → conexión y escritura en Google Sheets

   La función pública `revisar_perfiles_instagram(driver)` puede llamarse desde
   `main.py`, respetando el flag `ACTIVAR_REVISION_IG` en config.py.
"""

from __future__ import annotations

import random
import time
from typing import List
from selenium.webdriver.chrome.webdriver import WebDriver

from logger_config import logger
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
#   Función pública
# ---------------------------------------------------------------------------

def revisar_perfiles_instagram(driver: WebDriver, limite_perfiles: int | None = None):
    """Verifica perfiles IG listados en la hoja *IG‑IM*.

    Args
    ----
    driver : selenium.webdriver.Chrome
        Instancia de driver ya iniciada desde el módulo principal.

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

    procesados = 0
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

    logger.info("Revisión IG finalizada. %s perfiles procesados.", procesados)
