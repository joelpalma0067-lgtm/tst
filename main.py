import imaplib, smtplib, email, yt_dlp, time, os
from email.message import EmailMessage

# --- CONFIGURACIÓN ---
MI_CORREO = "zerokhyt@gmail.com"
MI_CLAVE_16 = "gkllljgczgycrwkd"

def descargar_contenido(asunto):
    # Railway ya tiene FFmpeg, así que aquí sí podemos bajar MP4 real
    es_video = "MP4" in asunto.upper()
    nombre_busqueda = asunto.replace("MP4", "").replace("mp4", "").strip()
    
    opciones = {
        'format': 'bestvideo+bestaudio/best' if es_video else 'bestaudio/best',
        'outtmpl': 'descarga.%(ext)s',
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(f"ytsearch1:{nombre_busqueda}", download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Error descarga: {e}")
        return None

def ejecutar():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(MI_CORREO, MI_CLAVE_16)
        mail.select("inbox")
        _, datos = mail.search(None, 'UNSEEN')
        
        for num in datos[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            asunto = msg["Subject"]
            remitente = msg["From"]
            
            print(f"📩 Petición: {asunto}")
            archivo = descargar_contenido(asunto)
            
            if archivo and os.path.exists(archivo):
                # Enviar correo (usando tu lógica de antes)
                print(f"✅ Enviado: {archivo}")
                os.remove(archivo)
            
            mail.store(num, '+FLAGS', '\\Seen')
        mail.logout()
    except Exception as e:
        print(f"Esperando... {e}")

if __name__ == "__main__":
    print("🤖 BOT EN RAILWAY INICIADO")
    while True:
        ejecutar()
        time.sleep(10)
