"""
revisar_respuestas.py
Flujo completo para:
- Ordenar contactos según méritos y participación previa (usando ordenar_por_prioridad_y_actualizar)
- Leer respuestas recibidas vía WhatsApp (simulado)
- Marcar 'Respondió' para quienes respondieron
- Asignar 'Entrada Gratis' a los primeros N según prioridad
- Actualizar 'Número de rezago' para quienes respondieron pero no ganaron
Requiere:
- sheets_utils.py con funciones para conexión y actualización de hoja
- config.py con configuraciones y columnas definidas
"""
import random
from sheets_utils import conectar_sheets, obtener_indices_columnas, escribir_en_celda
from config import COLUMNAS, FASE_ACTUAL, NUMERO_ENTRADAS_POR_FASE

def normalizar_telefono(tel):
    """Normaliza teléfono para comparación: solo dígitos."""
    return ''.join(filter(str.isdigit, str(tel)))

def parse_fases(fases_str):
    """
    Convierte cadena "1,2,5" a lista ['1','2','5'], ignorando no numéricos o vacíos.
    """
    if not fases_str:
        return []
    return [f.strip() for f in fases_str.split(',') if f.strip().isdigit()]

def ordenar_por_prioridad_y_actualizar(hoja_datos, columnas):
    """
    Ordena contactos según participación, asistencia y pases.
    Actualiza la columna 'Prioridad' en la hoja.
    Retorna la lista ordenada con datos y fila.
    """

    registros = hoja_datos.get_all_records()

    meritocracia = []
    sin_participacion = []

    for idx, c in enumerate(registros):
        fases_participadas = parse_fases(c.get(columnas["fases_participadas"], ""))
        recibio_pases = parse_fases(c.get(columnas["recibio_pase"], ""))
        asistio = int(c.get(columnas["asistio"], 0) or 0)

        registro = {
            "fila": idx + 2,  # +2 porque la fila 1 es encabezado
            "datos": c,
            "num_fases": len(fases_participadas),
            "num_asistencias": asistio,
            "num_pases": len(recibio_pases)
        }

        if registro["num_fases"] > 0:
            meritocracia.append(registro)
        else:
            sin_participacion.append(registro)

    # Orden rígido para quienes participaron
    contactos_merito = sorted(
        meritocracia,
        key=lambda x: (
            -x["num_fases"],
            -x["num_asistencias"],
            x["num_pases"]
        )
    )

    # Aleatorizar los que nunca participaron
    random.shuffle(sin_participacion)

    # Unión final: primero mérito, luego aleatorio
    orden_final = contactos_merito + sin_participacion

    # Actualizar la columna Prioridad
    col_prioridad = list(columnas.values()).index(columnas["prioridad"]) + 1
    for i, registro in enumerate(orden_final, start=1):
        escribir_en_celda(hoja_datos, registro["fila"], col_prioridad, i)

    return orden_final

def obtener_mensajes_whatsapp():
    """
    Simulación de lectura de mensajes WhatsApp.
    Debes reemplazarlo con tu implementación real.
    Retorna lista de (telefono, timestamp, mensaje).
    """
    mensajes_simulados = [
        ('5512345678', 1620000000, 'Quiero participar'),
        ('5598765432', 1620000500, '¡Cuenta conmigo!'),
        ('5511122233', 1620001000, 'Hola, me anoto'),
    ]
    return mensajes_simulados

def revisar_respuestas():
    hoja = conectar_sheets()
    columnas_idx = obtener_indices_columnas(hoja)
    registros = hoja.get_all_records()

    # 1. Ordenar contactos por prioridad y actualizar columna
    ordenados = ordenar_por_prioridad_y_actualizar(hoja, COLUMNAS)

    # 2. Obtener mensajes WhatsApp y normalizar teléfonos
    mensajes = obtener_mensajes_whatsapp()
    mensajes.sort(key=lambda x: x[1])  # Ordenar por tiempo ascendente
    telefonos_respondieron = [normalizar_telefono(t[0]) for t in mensajes]

    # 3. Crear mapa teléfono -> fila para rápido acceso
    telefono_a_fila = {}
    for r in ordenados:
        tel_norm = normalizar_telefono(r["datos"].get(COLUMNAS["telefono"], ""))
        if tel_norm:
            telefono_a_fila[tel_norm] = r["fila"]

    col_respondio = columnas_idx["respondio"]
    col_entrada = columnas_idx["entrada_gratis"]
    col_rezago = columnas_idx["numero_rezago"]

    ganadores = set()

    # 4. Marcar 'Respondió' para quienes respondieron
    for tel in telefonos_respondieron:
        if tel in telefono_a_fila:
            fila = telefono_a_fila[tel]
            escribir_en_celda(hoja, fila, col_respondio, True)

    # 5. Asignar 'Entrada Gratis' a primeros N según orden priorizado
    for idx, contacto in enumerate(ordenados):
        fila = contacto["fila"]
        tel = normalizar_telefono(contacto["datos"].get(COLUMNAS["telefono"], ""))
        respondio = tel in telefonos_respondieron

        if respondio and idx < NUMERO_ENTRADAS_POR_FASE:
            escribir_en_celda(hoja, fila, col_entrada, True)
            ganadores.add(tel)
        else:
            # Si respondió pero no ganó, marcar Entrada Gratis False
            if respondio:
                escribir_en_celda(hoja, fila, col_entrada, False)

                # Actualizar número de rezago agregando la fase actual
                registro = contacto["datos"]
                rezagos_previos = registro.get(COLUMNAS["numero_rezago"], "")
                fases = set(rezagos_previos.split(",")) if rezagos_previos else set()
                fases.add(str(FASE_ACTUAL))
                nuevo_rezago = ",".join(sorted(fases, key=int))
                escribir_en_celda(hoja, fila, col_rezago, nuevo_rezago)

    print(f"Proceso completado. Ganadores asignados: {len(ganadores)}")
    return ganadores

if __name__ == "__main__":
    revisar_respuestas()
