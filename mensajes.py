# mensajes.py

def mensaje_convocatoria_inicial(contacto):
    nombre = contacto.get("Nombre", "amig@")
    return f"""Hola {nombre}, ¡espero que estés muy bien!

¡Gracias por participar en *Instant Moments*, en alianza con *Cine Tonalá*!

🎁 Si eres una de *las primeras 30 personas en responder este mensaje tendrás una entrada gratis al cine*, válida del 3 al 31 de julio.

Consulta las funciones disponibles aquí 👉 https://www.cinetonala.mx/

🎉 Además, todos los que participaron en este proyecto obtendrán:

*2x1 en coctelería y bebidas.*  
Solo presenta tu foto las veces que quieras hasta Dic. 2025

Sígueme para estar al tanto de las dinámicas:  
📸 https://www.instagram.com/yoali.spindola/
"""

def mensaje_ganador_entrada(contacto):
    nombre = contacto.get("Nombre", "amig@")
    correo = contacto.get("Correo", "no especificado")
    instagram = contacto.get("Instagram", "no especificado")
    telefono = contacto.get("Teléfono", "no especificado")
    
    return f"""Participaste en *Instant Moments* y fuiste una de las primeras personas en responder.  
🎁 ¡Has ganado una entrada gratis al Cine Tonalá!

Consulta la cartelera y elige tu función 👉 https://www.cinetonala.mx/  
Si tienes intención de asistir, confírmame por este medio.  
Si no puedes o no te interesa, por favor avísame para poder regalar tu entrada a quien sigue 🙏

Confirma que tus datos estén correctos porque el pase será enviado por correo electrónico:

📌 Nombre: {nombre}  
📌 Correo: {correo}  
📌 Instagram: {instagram}  
📌 Teléfono: {telefono}

Gracias por formar parte de este proyecto 📸  
Sígueme para más dinámicas: https://www.instagram.com/yoali.spindola/
"""

def mensaje_cercano_a_ganador(contacto):
    nombre = contacto.get("Nombre", "amig@")
    numero_rezago = contacto.get("Número de rezago", None)
    return f"""Hola {nombre}, ¡gracias por participar en *Instant Moments*!  

Esta vez estuviste a solo {numero_rezago or "unos pocos"} mensajes de conseguir tu entrada gratis al cine 🎟️  
Pero hay buenas noticias:

🎯 Si alguno de los ganadores no reclama su pase, ¡iremos otorgándolos en orden!  
📩 Además, el próximo mes tú serás de los primeros en recibir el aviso para participar en la siguiente fase.

Gracias por tu presencia y energía, seguimos en contacto.  
📸 Sígueme para estar al tanto: https://www.instagram.com/yoali.spindola/
"""

def mensaje_integracion_futuras_fases(contacto):
    nombre = contacto.get("Nombre", "amig@")
    return f"""Hola {nombre}, gracias por ser parte de *Instant Moments* 📸  

Estoy organizando nuevas fases del proyecto y me encantaría que sigas participando 💫  
Para asegurar que recibas los avisos importantes, te pido algo muy simple:

📲 *Agrega mi contacto como "Yoali Spíndola" o "Instant Moments" en tu agenda.*  
WhatsApp a veces suspende mi cuenta por el volumen de mensajes durante las convocatorias,  
pero si ya me tienes registrado, eso no sucede 🙂

🎉 Además, recuerda que quienes participaron en este proyecto pueden disfrutar en *Cine Tonalá* de:

🍹 *2x1 en coctelería y bebidas*  
Solo presenta tu foto las veces que quieras hasta *diciembre 2025*

Para enterarte de nuevas dinámicas, fechas y lugares para tomarte fotos:  
📍 https://www.instagram.com/yoali.spindola/
"""

def mensaje_recordatorio_confirmacion(contacto):
    nombre = contacto.get("Nombre", "amig@")
    correo = contacto.get("Correo", "no proporcionado")
    instagram = contacto.get("Instagram", "no proporcionado")
    telefono = contacto.get("Teléfono", "no proporcionado")

    mensaje = f"""Hola {nombre},

Quiero recordarte que tu pase gratis es válido todo el mes para la función de cine que quieras, excluyendo eventos presenciales como stand-ups y obras de teatro.

No necesitas indicar cuál función elegir ni escoger asiento, solo presenta tu boleto digital en la entrada.

🧡 Es importante que confirmes tu correo, ya que es el medio que el cine usa para enviarte el pase. Hoy entregaré la lista y ojalá veas este mensaje.

Datos que tenemos registrados:  
📧 Correo: {correo}  
📸 Instagram: {instagram}  
📱 Teléfono: {telefono}

Estoy organizando nuevas fases del proyecto y me encantaría que sigas participando 💫  
Para asegurar que recibas los avisos importantes, te pido algo muy simple:

📲 *Agrega mi contacto como "Yoali Spíndola" o "Instant Moments" en tu agenda.*  
WhatsApp a veces suspende mi cuenta por el volumen de mensajes durante las convocatorias,  
pero si ya me tienes registrado, eso no sucede 🙂

🎉 Además, recuerda que quienes participaron en este proyecto pueden disfrutar en *Cine Tonalá* de:

🍹 *2x1 en coctelería y bebidas*  
Solo presenta tu foto las veces que quieras hasta *diciembre 2025*"""

#Para enterarte de nuevas dinámicas, fechas y lugares para tomarte fotos:  
#📍 https://www.instagram.com/yoali.spindola/

#Gracias por ser parte de *Instant Moments*."""

    return mensaje