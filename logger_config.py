import logging
import os

LOG_FILE = "app.log"

def configurar_logger():
    logger = logging.getLogger("instant_moments")
    logger.setLevel(logging.DEBUG)  # Puedes cambiar a INFO en producción

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Log en archivo
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Log en consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Evitar duplicados al reconfigurar
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = configurar_logger()