import random
import traceback
from logger_config import logger


def clasificar_contacto(contacto: dict) -> str:
    """Clasifica a un contacto de acuerdo con las combinaciones de
    los campos `Respondió` y `Entrada Gratis`.

    Retorna
    -------
    str
        - ``'ganador'``        → Respondió *y* tiene Entrada Gratis
        - ``'cercano'``        → Respondió, sin Entrada Gratis
        - ``'parcial'``        → No respondió, pero tiene Entrada Gratis
        - ``'no_interesado'``  → No respondió ni tiene Entrada Gratis
    """
    # Normalizamos posibles valores provenientes de Google Sheets (TRUE/FALSE, Sí/No, 1/0…)
    TRUE_VALUES = {True, "TRUE", "True", "1", 1, "Sí", "Si", "sí", "si"}
    respondio = contacto.get("Respondió") in TRUE_VALUES
    entrada_gratis = contacto.get("Entrada Gratis") in TRUE_VALUES

    if respondio and entrada_gratis:
        return "ganador"
    elif respondio:
        return "cercano"
    elif entrada_gratis:
        return "parcial"
    else:
        return "no_interesado"


def parse_fases(fases_str: str):
    """Convierte una cadena separada por comas (por ejemplo "1,2,5")
    en una *lista* de strings correspondientes a los números de fase.
    Entradas vacías o no‑numéricas se ignoran silenciosamente.
    """
    try:
        if not fases_str:
            return []
        return [f.strip() for f in fases_str.split(',') if f.strip().isdigit()]
    except Exception as e:
        logger.warning("Error en parse_fases con input '%s': %s", fases_str, e)
        return []


def ordenar_por_prioridad_y_actualizar(hoja_datos, columnas: dict):
    """Ordena los contactos por *mérito* y actualiza la columna «Prioridad».

    Criterios de mérito (en este orden):
    1. Cantidad de fases en las que ha participado (más → antes).
    2. Número de asistencias registradas (más → antes).
    3. Número de pases recibidos (menos → antes para favorecer a quien ha recibido menos beneficios).

    Contactos *sin* participación en fases se añaden al final del listado en orden aleatorio.
    """
    try:
        registros = hoja_datos.get_all_records()
    except Exception as e:
        logger.error("Error obteniendo registros de la hoja: %s", e)
        return []

    meritocracia: list[dict] = []
    sin_participacion: list[dict] = []

    for idx, contacto in enumerate(registros):
        try:
            fases_participadas = parse_fases(contacto.get(columnas["fases_participadas"], ""))
            recibio_pases = parse_fases(contacto.get(columnas["recibio_pase"], ""))
            asistio = int(contacto.get(columnas["asistio"], 0) or 0)

            registro = {
                "fila": idx + 2,  # +2 porque fila 1 es encabezado y get_all_records() empieza en 0
                "datos": contacto,
                "num_fases": len(fases_participadas),
                "num_asistencias": asistio,
                "num_pases": len(recibio_pases),
                # Clasificación por respuesta/entrada para usar en otros módulos si se requiere
                "clasificacion": clasificar_contacto(contacto),
            }

            (meritocracia if registro["num_fases"] > 0 else sin_participacion).append(registro)
        except Exception as e:
            logger.warning("Error procesando registro índice %s: %s", idx, e)
            logger.debug(traceback.format_exc())

    # --- Ordenamiento por mérito ---
    try:
        contactos_merito = sorted(
            meritocracia,
            key=lambda x: (
                -x["num_fases"],        # Más fases primero
                -x["num_asistencias"],  # Más asistencias
                x["num_pases"],         # Menos pases recibidos
            ),
        )
    except Exception as e:
        logger.error("Error ordenando contactos de mérito: %s", e)
        contactos_merito = meritocracia  # fallback sin ordenar

    # --- Sin participación: orden aleatorio ---
    try:
        random.shuffle(sin_participacion)
    except Exception as e:
        logger.warning("Error aleatorizando sin participación: %s", e)

    orden_final = contactos_merito + sin_participacion

    # --- Escribir la prioridad en la hoja ---
    try:
        col_prioridad_idx = list(columnas.values()).index(columnas["prioridad"]) + 1
    except Exception as e:
        logger.error("Error obteniendo índice de columna 'Prioridad': %s", e)
        col_prioridad_idx = None

    if col_prioridad_idx:
        for prioridad, registro in enumerate(orden_final, start=1):
            try:
                hoja_datos.update_cell(registro["fila"], col_prioridad_idx, prioridad)
            except Exception as e:
                logger.warning(
                    "Error actualizando prioridad fila %s: %s", registro["fila"], e
                )

    return [r["datos"] for r in orden_final]
