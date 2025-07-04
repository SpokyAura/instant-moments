# ---------------------------
# 📤 Qué mensajes enviar hoy
# ---------------------------
ENVIAR_MENSAJES_INICIALES = False
ENVIAR_RECORDATORIOS_CONFIRMACION = False
ENVIAR_MENSAJES_INTEGRACION = False
ENVIAR_MENSAJES_RESULTADOS = False

# ---------------------------
# 🔄 Fase actual del proyecto
# ---------------------------
FASE_ACTUAL = 1

# ---------------------------
# 🔐 Configuración general
# ---------------------------
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = 'tu_id_aqui'
HOJA_ACTIVA = 'W-IM'
CREDENTIALS_FILE = 'credenciales.json'

# ---------------------------
# 📊 Columnas del Sheet
# ---------------------------
COLUMNAS = {
    "añadio_contacto": "Añadió Contacto",
    "nombre": "Nombre",
    "correo": "Correo",
    "instagram": "Instagram",
    "telefono": "Teléfono",
    "mensaje_enviado_wa": "Mensaje enviado WA",
    "fecha_envio_wa": "Fecha de envío WA",
    "hora_envio_wa": "Hora de envío WA",
    "mensaje_enviado_ig": "Mensaje enviado IG",
    "fecha_envio_ig": "Fecha de envío IG",
    "hora_envio_ig": "Hora de envío IG",
    "respondio": "Respondió",
    "entrada_gratis": "Entrada Gratis",
    "interes": "Interés",
    "zona": "Zona / Segmento",
    "proxima_accion": "Próxima acción",
    "comentarios": "Comentarios / Seguimiento",
    "correo_verificado": "Correo Verificado",
    "fases_participadas": "Fases participadas"
}

MENSAJES = {
    "mensaje_enviado": "Mensaje enviado",
    "error_envio": "Error al enviar",
    "accion_incluir_relacion_cine": "Incluir en Relación para el cine",
    # agrega más mensajes parametrizados aquí...
}