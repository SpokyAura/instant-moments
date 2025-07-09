import random
import traceback
from logger_general import logger  # Ajusta el nombre y ruta según tu proyecto

def parse_fases(fases_str):
    """
    Convierte una cadena separada por comas (como "1,2,5") en una lista de strings.
    Ignora entradas vacías o no numéricas.
    """
    try:
        if not fases_str:
            return []
        return [f.strip() for f in fases_str.split(',') if f.strip().isdigit()]
    except Exception as e:
        logger.warning(f"Error en parse_fases con input '{fases_str}': {e}")
        return []

def ordenar_por_prioridad_y_actualizar(hoja_datos, columnas):
    """
    Ordena los contactos según los criterios de participación, asistencia y pases recibidos.
    Asigna un número de prioridad a cada contacto y actualiza la hoja en la columna 'Prioridad'.
    Los que nunca han participado se colocan al final en orden aleatorio.
    """
    try:
        registros = hoja_datos.get_all_records()
    except Exception as e:
        logger.error(f"Error obteniendo registros de la hoja: {e}")
        return []

    meritocracia = []
    sin_participacion = []

    for idx, c in enumerate(registros):
        try:
            fases_participadas = parse_fases(c.get(columnas["fases_participadas"], ""))
            recibio_pases = parse_fases(c.get(columnas["recibio_pase"], ""))
            asistio = int(c.get(columnas["asistio"], 0) or 0)

            registro = {
                "fila": idx + 2,  # +2 porque la hoja empieza en 1 y fila 1 es encabezado
                "datos": c,
                "num_fases": len(fases_participadas),
                "num_asistencias": asistio,
                "num_pases": len(recibio_pases)
            }

            if registro["num_fases"] > 0:
                meritocracia.append(registro)
            else:
                sin_participacion.append(registro)

        except Exception as e:
            logger.warning(f"Error procesando registro índice {idx}: {e}")
            logger.debug(traceback.format_exc())

    try:
        contactos_merito = sorted(
            meritocracia,
            key=lambda x: (
                -x["num_fases"],
                -x["num_asistencias"],
                x["num_pases"]
            )
        )
    except Exception as e:
        logger.error(f"Error ordenando contactos de mérito: {e}")
        contactos_merito = meritocracia  # fallback sin ordenar

    try:
        random.shuffle(sin_participacion)
    except Exception as e:
        logger.warning(f"Error aleatorizando sin participación: {e}")

    orden_final = contactos_merito + sin_participacion

    try:
        col_prioridad = list(columnas.values()).index(columnas["prioridad"]) + 1
    except Exception as e:
        logger.error(f"Error obteniendo índice de columna 'Prioridad': {e}")
        col_prioridad = None

    if col_prioridad:
        for i, registro in enumerate(orden_final, start=1):
            try:
                hoja_datos.update_cell(registro["fila"], col_prioridad, i)
            except Exception as e:
                logger.warning(f"Error actualizando prioridad fila {registro['fila']}: {e}")

    return [r["datos"] for r in orden_final]
