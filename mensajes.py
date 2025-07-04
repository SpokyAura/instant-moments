# mensajes.py

def mensaje_convocatoria_inicial(nombre):
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

def mensaje_ganador_entrada(nombre, correo, instagram, telefono):
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

def mensaje_cercano_a_ganador(nombre, numero_rezago=None):
    return f"""Hola {nombre}, ¡gracias por participar en *Instant Moments*!  

Esta vez estuviste a solo {numero_rezago or "unos pocos"} mensajes de conseguir tu entrada gratis al cine 🎟️  
Pero hay buenas noticias:

🎯 Si alguno de los ganadores no reclama su pase, ¡iremos otorgándolos en orden!  
📩 Además, el próximo mes tú serás de los primeros en recibir el aviso para participar en la siguiente fase.

Gracias por tu presencia y energía, seguimos en contacto.  
📸 Sígueme para estar al tanto: https://www.instagram.com/yoali.spindola/
"""

def mensaje_integracion_futuras_fases(nombre):
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

def mensaje_recordatorio_confirmacion(nombre, correo, instagram, telefono):
    return f"""Hola {nombre}, solo paso a recordarte que fuiste seleccionad@ para recibir una entrada gratis por participar en *Instant Moments* 🎉  

Aún no he recibido tu confirmación, y *hoy mismo* entregaré la lista final al *Cine Tonalá*.  
Necesito incluir tu correo porque ahí se enviará tu entrada 🎟️📩

Confírmame si vas a asistir y que estos datos sean correctos:

📌 Nombre: {nombre}  
📌 Correo: {correo}  
📌 Instagram: {instagram}  
📌 Teléfono: {telefono}

🎬 El pase será válido para cualquier función de cine durante todo julio  
(*excepto eventos presenciales como stand-up u obras de teatro*).  
No necesitas escoger función ni asiento: solo preséntate con tu boleto digital.

🍹 Además, recuerda que tienes *2x1 en coctelería y bebidas* mostrando tu foto,  
las veces que quieras hasta *diciembre 2025*.

Gracias por ser parte de este proyecto 📸  
Para estar al tanto de nuevas dinámicas, fechas y lugares para tomarte fotos, sígueme en Instagram:  
👉 https://www.instagram.com/yoali.spindola/

Espero tu respuesta pronto 🙂
"""