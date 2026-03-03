import imaplib, smtplib, email, yt_dlp, time, os
from email.message import EmailMessage

# --- CONFIGURACIÓN ---
MI_CORREO = "zerokhyt@gmail.com"
MI_CLAVE_16 = "wblebsdaercnceav"

def descargar_audio(asunto):
    # Quitamos "MP4" del asunto para que YouTube no sospeche
    nombre_limpio = asunto.replace("MP4", "").replace("mp4", "").strip()
    
    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': 'musica.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        # --- EL ESCUDO ANTI-BOT ---
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        # ---------------------------
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        print(f"📥 Intentando descargar audio para: {nombre_limpio}...")
        with yt_dlp.YoutubeDL(opciones) as ydl:
            # Buscamos directamente el término
            info = ydl.extract_info(f"ytsearch1:{nombre_limpio}", download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"❌ Error de YouTube: {e}")
        return None

def ejecutar_bot():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(MI_CORREO, MI_CLAVE_16)
        mail.select("inbox")
        
        # BUSCA CORREOS NO LEÍDOS
        _, datos = mail.search(None, 'UNSEEN')
        
        for num in datos[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            asunto = msg["Subject"]
            remitente = msg["From"]
            
            print(f"📩 Petición detectada: {asunto}")
            archivo = descargar_audio(asunto)
            
            if archivo and os.path.exists(archivo):
                print(f"📧 Enviando archivo a {remitente}...")
                respuesta = EmailMessage()
                respuesta['Subject'] = f"🎵 Tu audio: {asunto}"
                respuesta['From'] = MI_CORREO
                respuesta['To'] = remitente
                respuesta.set_content(f"Aquí tienes el audio de: {asunto}")
                
                with open(archivo, 'rb') as f:
                    respuesta.add_attachment(f.read(), maintype='audio', subtype='mpeg', filename=os.path.basename(archivo))
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(MI_CORREO, MI_CLAVE_16)
                    smtp.send_message(respuesta)
                
                os.remove(archivo)
                print("✅ ¡Enviado con éxito!")
            
            # Marcar como leído
            mail.store(num, '+FLAGS', '\\Seen')
        mail.logout()
    except Exception as e:
        print(f"🔍 Revisando... {e}")

if __name__ == "__main__":
    print("🚀 BOT DE AUDIO (ANTI-BLOQUEO) INICIADO")
    while True:
        ejecutar_bot()
        time.sleep(10)





