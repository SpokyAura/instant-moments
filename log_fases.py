import csv
from datetime import datetime
from config import LOG_DATOS

LOG_FILE = "log_fases.csv"

def inicializar_log():
    if not LOG_DATOS:
        return
    try:
        with open(LOG_FILE, mode='x', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Fecha", "Fase", "Mensajes Enviados", "Respuestas Recibidas", 
                "Entradas Gratis Entregadas", "Contactos sin Teléfono",
                "Ganadores sin Confirmar", "Porcentaje Conversión (%)", "Comentarios"
            ])
    except FileExistsError:
        pass

def registrar_estadistica(
    fase,
    mensajes_enviados,
    respuestas_recibidas,
    entradas_gratis,
    comentarios="",
    sin_numero=0,
    ganadores_no_confirmaron=0,
    porcentaje_conversion=None
):
    if not LOG_DATOS:
        return

    # Leer todas las filas existentes excepto la de esta fase
    try:
        with open(LOG_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            filas = [row for row in reader if row["Fase"] != str(fase)]
    except FileNotFoundError:
        filas = []

    # Preparar nueva fila
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fila_log = {
        "Fecha": fecha,
        "Fase": str(fase),
        "Mensajes Enviados": str(mensajes_enviados),
        "Respuestas Recibidas": str(respuestas_recibidas),
        "Entradas Gratis Entregadas": str(entradas_gratis),
        "Contactos sin Teléfono": str(sin_numero),
        "Ganadores sin Confirmar": str(ganadores_no_confirmaron),
        "Porcentaje Conversión (%)": f"{porcentaje_conversion:.2f}" if porcentaje_conversion is not None else "",
        "Comentarios": comentarios
    }

    filas.append(fila_log)

    # Escribir todo de nuevo
    with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
        campos = [
            "Fecha", "Fase", "Mensajes Enviados", "Respuestas Recibidas",
            "Entradas Gratis Entregadas", "Contactos sin Teléfono",
            "Ganadores sin Confirmar", "Porcentaje Conversión (%)", "Comentarios"
        ]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(filas)

    # Imprimir resumen en consola
    print("\n📈 RESUMEN DE LA FASE:")
    print(f"📅 Fecha de registro: {fecha}")
    print(f"🌀 Fase: {fase}")
    print(f"✉️ Mensajes enviados: {mensajes_enviados}")
    print(f"✅ Respuestas recibidas: {respuestas_recibidas}")
    print(f"🎟️ Entradas gratis entregadas: {entradas_gratis}")
    print(f"📵 Contactos sin teléfono: {sin_numero}")
    print(f"⏳ Ganadores sin confirmar asistencia: {ganadores_no_confirmaron}")
    if porcentaje_conversion is not None:
        print(f"📊 Porcentaje de conversión: {porcentaje_conversion:.2f}%")
        if porcentaje_conversion < 25:
            print("⚠️ Advertencia: Conversión baja. Revisa el mensaje de convocatoria o tiempos de envío.")
    if comentarios:
        print(f"🗒️ Comentarios: {comentarios}")
    print("✅ Estadísticas registradas en log_fases.csv\n")