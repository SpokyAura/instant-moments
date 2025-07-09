import random
import traceback
from sheets_utils import conectar_sheets, obtener_indices_columnas, escribir_en_celda
from config import COLUMNAS, FASE_ACTUAL, NUMERO_ENTRADAS_POR_FASE
from whatsapp_lector import obtener_mensajes_whatsapp_desde_selenium as obtener_mensajes_whatsapp
from logger_config import logger

def normalizar_telefono(tel):
    try:
        return ''.join(filter(str.isdigit, str(tel)))
    except Exception as e:
        logger.warning(f"Error normalizando teléfono '{tel}': {e}")
        return ""

def parse_fases(fases_str):
    try:
        if not fases_str:
            return []
        return [f.strip() for f in fases_str.split(',') if f.strip().isdigit()]
    except Exception as e:
        logger.warning(f"Error parseando fases '{fases_str}': {e}")
        return []

def ordenar_por_prioridad_y_actualizar(hoja_datos, columnas):
    try:
        registros = hoja_datos.get_all_records()
        meritocracia = []
        sin_participacion = []

        for idx, c in enumerate(registros):
            try:
                fases_participadas = parse_fases(c.get(columnas["fases_participadas"], ""))
                recibio_pases = parse_fases(c.get(columnas["recibio_pase"], ""))
                asistio = int(c.get(columnas["asistio"], 0) or 0)

                registro = {
                    "fila": idx + 2,
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

        contactos_merito = sorted(
            meritocracia,
            key=lambda x: (-x["num_fases"], -x["num_asistencias"], x["num_pases"])
        )

        random.shuffle(sin_participacion)
        orden_final = contactos_merito + sin_participacion

        try:
            col_prioridad = list(columnas.values()).index(columnas["prioridad"]) + 1
        except Exception as e:
            logger.error(f"Error encontrando columna Prioridad: {e}")
            return orden_final

        for i, registro in enumerate(orden_final, start=1):
            try:
                escribir_en_celda(hoja_datos, registro["fila"], col_prioridad, i)
            except Exception as e:
                logger.warning(f"Error actualizando prioridad fila {registro['fila']}: {e}")

        return orden_final
    except Exception as e:
        logger.error(f"Error en ordenar_por_prioridad_y_actualizar: {e}")
        logger.debug(traceback.format_exc())
        return []

def revisar_respuestas():
    try:
        hoja = conectar_sheets()
        columnas_idx = obtener_indices_columnas(hoja)
        registros = hoja.get_all_records()

        ordenados = ordenar_por_prioridad_y_actualizar(hoja, COLUMNAS)

        mensajes = obtener_mensajes_whatsapp()
        mensajes.sort(key=lambda x: x[1])

        telefono_orden = {}
        orden_actual_max = 0

        col_orden_respuesta = columnas_idx.get("orden_respuesta")

        for r in registros:
            try:
                valor = r.get(COLUMNAS["orden_respuesta"], "")
                if str(valor).strip().isdigit():
                    orden_actual_max = max(orden_actual_max, int(valor))
            except Exception:
                pass

        nuevos_mensajes = []

        for tel, _, _ in mensajes:
            tel_norm = normalizar_telefono(tel)
            if tel_norm not in telefono_orden:
                orden_actual_max += 1
                telefono_orden[tel_norm] = orden_actual_max
                nuevos_mensajes.append((tel_norm, orden_actual_max))

        telefono_a_fila = {}
        for r in ordenados:
            try:
                tel_norm = normalizar_telefono(r["datos"].get(COLUMNAS["telefono"], ""))
                if tel_norm:
                    telefono_a_fila[tel_norm] = r["fila"]
            except Exception as e:
                logger.warning(f"Error creando mapa teléfono->fila fila {r.get('fila')}: {e}")

        col_respondio = columnas_idx.get("respondio")
        col_entrada = columnas_idx.get("entrada_gratis")
        col_rezago = columnas_idx.get("numero_rezago")

        ganadores = set()

        for tel, orden_resp in nuevos_mensajes:
            if tel in telefono_a_fila:
                fila = telefono_a_fila[tel]
                try:
                    escribir_en_celda(hoja, fila, col_respondio, True)
                    if col_orden_respuesta:
                        escribir_en_celda(hoja, fila, col_orden_respuesta, orden_resp)
                except Exception as e:
                    logger.warning(f"Error actualizando fila {fila}: {e}")

        respondieron = [
            (tel, orden) for tel, orden in telefono_orden.items() if tel in telefono_a_fila
        ]
        respondieron.sort(key=lambda x: x[1])

        ultimos_n = respondieron[-NUMERO_ENTRADAS_POR_FASE:] if len(respondieron) >= NUMERO_ENTRADAS_POR_FASE else respondieron
        set_ganadores = set(tel for tel, _ in ultimos_n)

        max_orden = max(orden for _, orden in ultimos_n) if ultimos_n else 0

        for contacto in ordenados:
            fila = contacto["fila"]
            try:
                tel = normalizar_telefono(contacto["datos"].get(COLUMNAS["telefono"], ""))
                if tel in telefono_orden:
                    orden_resp = telefono_orden[tel]
                    if tel in set_ganadores:
                        escribir_en_celda(hoja, fila, col_entrada, True)
                        escribir_en_celda(hoja, fila, col_rezago, "")
                        ganadores.add(tel)
                    else:
                        escribir_en_celda(hoja, fila, col_entrada, False)
                        rezago = max_orden - orden_resp
                        escribir_en_celda(hoja, fila, col_rezago, str(rezago))
            except Exception as e:
                logger.warning(f"Error procesando fila {fila}: {e}")

        logger.info(f"Proceso completado. Ganadores asignados: {len(ganadores)}")
        return ganadores

    except Exception as e:
        logger.error(f"Error general en revisar_respuestas: {e}")
        logger.debug(traceback.format_exc())
        return set()

if __name__ == "__main__":
    revisar_respuestas()
