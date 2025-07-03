import gspread
from google.oauth2.service_account import Credentials

# Autenticación
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(r'C:\bin\instant-moments\pivotal-mode-464204-t6-673f1678ee71.json', scopes=SCOPES)
client = gspread.authorize(creds)

# Abrir hoja
sheet = client.open_by_key("15kXq5wrYb9gJ0afeq_l82Fhj956gQryS1mB8OmzT5hI")
worksheet = sheet.worksheet("W-IM")

# Obtener todas las filas como listas (incluye celdas vacías)
todas_las_filas = worksheet.get_all_values()

# Tomar la cabecera
headers = todas_las_filas[0]

# Filtrar filas con valor en la primera columna (Nombre)
filas_utiles = [fila for fila in todas_las_filas[1:] if fila[1].strip() != ""]

# Convertir a lista de diccionarios (como get_all_records)
datos_filtrados = [dict(zip(headers, fila)) for fila in filas_utiles]

def crear_mensaje(nombre, correo, instagram, telefono, zona):
    zona_normalizada = zona.strip().lower()
    idioma = "Inglés" if zona_normalizada == "extranjero" else "Español"

    if idioma == "Español":
        saludo = f"Hola {nombre}, ¡espero que estés muy bien!"
        cuerpo = (
            "Muchas gracias por participar en Instant Moments. "
            "Antes de enviarte más información, quiero confirmar que tus datos estén correctos "
            "y saber si te gustaría participar en la primera quincena de entradas gratis para una función en Cine Tonalá.\n\n"
            "Las proyecciones disponibles serán entre el **1 y el 15 de julio**, puedes consultarlas aquí:\n"
            "👉 https://www.cinetonala.mx/\n\n"
            "Por favor, verifica que esta información esté correcta:"
        )
        tabla = (
            f"• Nombre: {nombre}\n"
            f"• Correo: {correo}\n"
            f"• Instagram: {instagram}\n"
            f"• Teléfono: {telefono}\n"
            f"• Idioma sugerido: {idioma}"
        )
        cierre = (
            "\n\nEs muy importante que me respondas para poder incluirte en los mensajes de seguimiento. "
            "También te invito a seguirme en Instagram 👉 https://www.instagram.com/yoali.spindola/"
        )

    else:  # Inglés
        saludo = f"Hi {nombre}, I hope you're doing great!"
        cuerpo = (
            "Thank you so much for participating in Instant Moments. "
            "Before I send you more information, I want to make sure your contact details are correct "
            "and to know if you’d like to join the first round of free tickets for a screening at Cine Tonalá.\n\n"
            "The screenings will take place between **July 1st and 15th**, you can check the schedule here:\n"
            "👉 https://www.cinetonala.mx/\n\n"
            "Please check that the following information is accurate:"
        )
        tabla = (
            f"• Name: {nombre}\n"
            f"• Email: {correo}\n"
            f"• Instagram: {instagram}\n"
            f"• Phone: {telefono}\n"
            f"• Suggested language: {idioma}"
        )
        cierre = (
            "\n\nIt's very important that you reply so I can include you in future updates. "
            "You can also follow me on Instagram 👉 https://www.instagram.com/yoali.spindola/"
        )

    return f"{saludo}\n\n{cuerpo}\n\n{tabla}{cierre}"

def test_mensaje(nombre_buscado, lista_contactos):
    for contacto in lista_contactos:
        nombre = contacto.get("Nombre", "").strip()
        if nombre.lower() == nombre_buscado.lower():
            correo = contacto.get("Correo", "").strip()
            instagram = contacto.get("Instagram", "").strip()
            telefono = contacto.get("Teléfono", "").strip()
            zona = contacto.get("Zona", "").strip()

            mensaje = crear_mensaje(nombre, correo, instagram, telefono, zona)

            print(f"Mensaje generado para {nombre}:\n{'-' * 50}")
            print(mensaje)
            print('-' * 50)
            return

    print(f"No se encontró ningún contacto con el nombre: {nombre_buscado}")

# Reemplaza con el nombre real de alguien del CRM (tal como aparece en la hoja)
test_mensaje("Isabel Suarez", datos_filtrados)