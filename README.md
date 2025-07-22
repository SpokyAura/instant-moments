# Instant Moments 📸✨

Automatación creativa para conectar con personas a través de WhatsApp, Instagram y Google Sheets. Este sistema fue creado para gestionar campañas artísticas interactivas, como la participación en instalaciones fotográficas, activaciones urbanas y dinámicas de selección.

---

## 🚀 Características

- 📩 Envío automatizado de mensajes por WhatsApp Web (Selenium)
- 📷 Validación de perfiles de Instagram (con BeautifulSoup/Selenium)
- 📊 Lectura y escritura en Google Sheets (vía gspread y Google API)
- 🎯 Clasificación y priorización de participantes por interés y respuestas
- 🧠 Registro automático de interacciones y seguimiento personalizado

---

## 🧰 Requisitos

- Python 3.10+
- Google Chrome (y chromedriver instalado)
- Cuenta de Google con acceso a la hoja de cálculo
- Cuenta de WhatsApp y/o Instagram activas

Librerías (ver `requirements.txt`):
- `selenium`
- `gspread`
- `oauth2client`
- `pandas`
- `python-dotenv` (opcional, para variables de entorno)

---

## 🔧 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/SpokyAura/instant-moments.git
cd instant-moments
```

2. Crea un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # en Unix/macOS
venv\Scripts\activate     # en Windows
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las credenciales de Google Sheets:
- Crea un proyecto en Google Cloud.
- Habilita la API de Google Sheets.
- Descarga el archivo `credentials.json` y colócalo en la raíz del proyecto.
- Comparte la hoja con el correo del cliente de servicio.

5. Crea y personaliza el archivo `config.py` (o usa `.env` si lo prefieres).

---

## 🛠️ Uso

1. Abre WhatsApp Web en una ventana de Chrome.  
2. Ejecuta el script principal:
```bash
python auto_im.py
```

El programa tomará los datos desde Google Sheets y gestionará el envío de mensajes, el seguimiento y el registro de respuestas.

Puedes ejecutar directamente otros módulos según tus necesidades:  
- `revisar_respuestas.py`: escanea mensajes no leídos y actualiza la hoja.  
- `orden_prioridad.py`: ajusta la lógica de interés.  
- `mensajes.py`: personaliza los textos que se envían.

---

## 🗂️ Estructura del proyecto

```
instant-moments/
│
├── auto_im.py                # Script principal
├── config.py                 # Configuración local
├── envio_mensajes.py         # Envío centralizado por WhatsApp
├── mensajes.py               # Mensajes personalizados
├── revisar_respuestas.py     # Análisis de respuestas nuevas
├── sheets_utils.py           # Conexión y lógica con Google Sheets
├── wa_ig_login.py            # Inicio de sesión automatizado
├── whatsapp_lector.py        # Lector de mensajes no leídos
├── log_fases.py              # Registro de fases y actividad
├── logger_config.py          # Configuración de logs
├── requirements.txt          # Dependencias
└── credentials.json          # Claves para Google Sheets (no compartir)
```

---

## 🔒 Seguridad

- No subas tu `credentials.json` ni datos sensibles al repositorio.  
- Usa variables de entorno o archivos `.env` para manejar claves y rutas.  
- Asegúrate de que `config.py` y `credentials.json` estén en `.gitignore`.

---

## 🙌 Créditos

Desarrollado por [SpokyAura](https://github.com/SpokyAura) como parte del proyecto artístico **Instant Moments**.

---

## 🪪 Licencia

Distribuido bajo la [Licencia MIT](LICENSE).
