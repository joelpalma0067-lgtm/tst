import imaplib, smtplib, email, yt_dlp, time, os
from email.header import decode_header
from email.message import EmailMessage

# --- CONFIGURACIÓN ---
MI_CORREO = "zerokhyt@gmail.com"
MI_CLAVE_16 = "ifjxwcsnyoledofe"

def decodificar_texto(texto):
    if not texto: return "Sin_Asunto"
    decoded, encoding = decode_header(texto)[0]
    if isinstance(decoded, bytes): 
        return decoded.decode(encoding if encoding else 'utf-8')
    return decoded

def descargar_contenido(asunto):
    es_video = "MP4" in asunto.upper()
    nombre_busqueda = asunto.replace("MP4", "").replace("mp4", "").strip()
    
    # Railway permite mejores descargas, pero usamos 'best' para evitar líos de FFmpeg
    opciones = {
        'format': 'best', 
        'outtmpl': 'descarga.%(ext)s',
        'noplaylist': True,
        'quiet': False, # Dejamos esto en False para ver el progreso en los logs de Railway
        'no_warnings': False,
        'retries': 5
    }

    try:
        print(f"📥 Buscando y descargando: {nombre_busqueda}...")
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(f"ytsearch1:{nombre_busqueda}", download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"❌ Error en yt-dlp: {e}")
        return None

def enviar_respuesta(destinatario, ruta_archivo, asunto_original):
    if not ruta_archivo or not os.path.exists(ruta_archivo):
        print("🚫 Error: El archivo no se creó. Abortando envío.")
        return

    msg = EmailMessage()
    msg['From'] = MI_CORREO
    msg['To'] = destinatario
    
    try:
        peso_mb = os.path.getsize(ruta_archivo) / (1024 * 1024)
        if peso_mb > 24:
            msg['Subject'] = "⚠️ Archivo muy pesado"
            msg.set_content(f"El archivo '{asunto_original}' pesa {peso_mb:.1f}MB y supera el límite de Gmail.")
        else:
            msg['Subject'] = f"📦 Aquí tienes: {asunto_original}"
            msg.set_content(f"¡Listo! Se descargó '{asunto_original}' correctamente.")
            
            tipo = 'video' if ruta_archivo.endswith('.mp4') else 'audio'
            with open(ruta_archivo, 'rb') as f:
                msg.add_attachment(f.read(), maintype=tipo, subtype='mp4', filename=os.path.basename(ruta_archivo))

        print(f"📧 Enviando correo a {destinatario}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MI_CORREO, MI_CLAVE_16)
            smtp.send_message(msg)
        print("✅ ¡Correo enviado con éxito!")
        
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")
    finally:
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
            print("🗑️ Archivo temporal eliminado.")

def monitorear():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(MI_CORREO, MI_CLAVE_16)
        mail.select("inbox")
        
        # Buscamos correos NO LEÍDOS
        _, datos = mail.search(None, 'UNSEEN')
        correos = datos[0].split()
        
        if not correos:
            print("🔍 No hay correos nuevos.")
            return

        for num in correos:
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            asunto = decodificar_texto(msg["subject"])
            remitente = msg["From"]
            
            print(f"📩 Nueva petición detectada: {asunto}")
            archivo_final = descargar_contenido(asunto)
            
            if archivo_final:
                enviar_respuesta(remitente, archivo_final, asunto)
            
            # Marcar como leído para no procesarlo dos veces
            mail.store(num, '+FLAGS', '\\Seen')
            
        mail.logout()
    except Exception as e:
        print(f"⚠️ Error de conexión/login: {e}")

if __name__ == "__main__":
    print("🚀 --- BOT INICIADO EN LA NUBE (RAILWAY) ---")
    while True:
        monitorear()
        print("💤 Esperando 10 segundos para la siguiente revisión...")
        time.sleep(10)


