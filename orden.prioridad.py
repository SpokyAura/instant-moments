import random

def parse_fases(fases_str):
    """
    Convierte una cadena separada por comas (como "1,2,5") en una lista de strings.
    Ignora entradas vacías o no numéricas.
    """
    if not fases_str:
        return []
    return [f.strip() for f in fases_str.split(',') if f.strip().isdigit()]

def ordenar_por_prioridad_y_actualizar(hoja_datos, columnas):
    """
    Ordena los contactos según los criterios de participación, asistencia y pases recibidos.
    Asigna un número de prioridad a cada contacto y actualiza la hoja en la columna 'Prioridad'.
    Los que nunca han participado se colocan al final en orden aleatorio.
    """
    registros = hoja_datos.get_all_records()

    meritocracia = []
    sin_participacion = []

    for idx, c in enumerate(registros):
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

    # Orden rígido para quienes ya participaron
    contactos_merito = sorted(
        meritocracia,
        key=lambda x: (
            -x["num_fases"],
            -x["num_asistencias"],
            x["num_pases"]
        )
    )

    # Aleatorizar solo los que no han participado nunca
    random.shuffle(sin_participacion)

    # Unir listas: primero los de mérito, luego los nuevos
    orden_final = contactos_merito + sin_participacion

    # Escribir prioridad en la hoja
    col_prioridad = list(columnas.values()).index(columnas["prioridad"]) + 1
    for i, registro in enumerate(orden_final, start=1):
        hoja_datos.update_cell(registro["fila"], col_prioridad, i)

    return [r["datos"] for r in orden_final]