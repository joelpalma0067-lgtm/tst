import imaplib, smtplib, email, yt_dlp, time, os
from email.message import EmailMessage

# --- CONFIGURACIÓN ---
MI_CORREO = "joelpalma0067@gmail.com"
MI_CLAVE_16 = "bjwowewrjcetjmlw" # Asegúrate que sea la de 16 letras de Google

def descargar_solo_audio(asunto):
    busqueda = asunto.replace("MP4", "").replace("mp4", "").strip()
    
    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio_local.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        # Este User-Agent es el que hizo que te funcionara la prueba recién
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    try:
        print(f"📥 Descargando: {busqueda}...")
        with yt_dlp.YoutubeDL(opciones) as ydl:
            # Usamos ytsearch para que busque el nombre que mandaste por correo
            info = ydl.extract_info(f"ytsearch1:{busqueda}", download=True)
            if 'entries' in info:
                return ydl.prepare_filename(info['entries'][0])
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"❌ Error al bajar de YouTube: {e}")
        return None

def ejecutar_bot():
    try:
        # 1. Conexión a Gmail
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(MI_CORREO, MI_CLAVE_16)
        mail.select("inbox")
        
        # 2. Buscar correos no leídos
        _, datos = mail.search(None, 'UNSEEN')
        
        for num in datos[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            asunto = msg["Subject"]
            remitente = msg["From"]
            
            print(f"📩 Nuevo correo de {remitente}: {asunto}")
            
            # 3. Descargar
            archivo = descargar_solo_audio(asunto)
            
            if archivo and os.path.exists(archivo):
                # 4. Enviar de vuelta
                print(f"📧 Enviando archivo...")
                respuesta = EmailMessage()
                respuesta['Subject'] = f"✅ Aquí tienes: {asunto}"
                respuesta['From'] = MI_CORREO
                respuesta['To'] = remitente
                respuesta.set_content(f"Se descargó correctamente: {asunto}")
                
                with open(archivo, 'rb') as f:
                    respuesta.add_attachment(
                        f.read(), 
                        maintype='audio', 
                        subtype='octet-stream', 
                        filename=os.path.basename(archivo)
                    )
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(MI_CORREO, MI_CLAVE_16)
                    smtp.send_message(respuesta)
                
                os.remove(archivo) # Limpia tu carpeta de VS Code
                print("✨ Proceso terminado con éxito.")
            
            # Marcar como leído para no repetir
            mail.store(num, '+FLAGS', '\\Seen')
            
        mail.logout()
    except Exception as e:
        # Si no hay correos, imprimirá esto cada 10 segundos
        print(f"🔎 Buscando correos... (Error si lo hay: {e})")

if __name__ == "__main__":
    print("📻 Bot de Audio Local Iniciado (Presiona Ctrl+C para detener)")
    while True:
        ejecutar_bot()
        time.sleep(10) # En PC podemos revisar más seguido que en la nube