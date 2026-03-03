import imaplib, smtplib, email, yt_dlp, time, os
from email.message import EmailMessage

# --- CONFIGURACIÓN ---
MI_CORREO = "zerokhyt@gmail.com"
MI_CLAVE_16 = "gkllljgczgycrwkd"

def descargar_audio(asunto):
    # Buscamos solo el audio de mejor calidad
    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': 'musica.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if os.name == 'posix' else [], # Railway tiene ffmpeg, tu PC quizás no
    }

    try:
        print(f"📥 Descargando audio para: {asunto}...")
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(f"ytsearch1:{asunto}", download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"❌ Error yt-dlp: {e}")
        return None

def ejecutar_bot():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(MI_CORREO, MI_CLAVE_16)
        mail.select("inbox") # Volvemos a inbox por simplicidad
        
        # BUSCA CORREOS NO LEÍDOS
        _, datos = mail.search(None, 'UNSEEN')
        
        for num in datos[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            asunto = msg["Subject"]
            remitente = msg["From"]
            
            print(f"📩 Petición recibida: {asunto}")
            archivo = descargar_audio(asunto)
            
            if archivo and os.path.exists(archivo):
                print(f"📧 Enviando MP3 a {remitente}...")
                respuesta = EmailMessage()
                respuesta['Subject'] = f"🎵 Aquí tienes: {asunto}"
                respuesta['From'] = MI_CORREO
                respuesta['To'] = remitente
                respuesta.set_content(f"Disfruta tu audio de: {asunto}")
                
                with open(archivo, 'rb') as f:
                    respuesta.add_attachment(f.read(), maintype='audio', subtype='mpeg', filename=os.path.basename(archivo))
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(MI_CORREO, MI_CLAVE_16)
                    smtp.send_message(respuesta)
                
                os.remove(archivo)
                print("✅ ¡Enviado y limpiado!")
            
            mail.store(num, '+FLAGS', '\\Seen')
        mail.logout()
    except Exception as e:
        print(f"🔍 Revisando... (Si no hay correos nuevos, este mensaje es normal)")

if __name__ == "__main__":
    print("🚀 BOT DE AUDIO INICIADO EN LA NUBE")
    while True:
        ejecutar_bot()
        time.sleep(30)



