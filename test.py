import imaplib, smtplib, email, yt_dlp, time, os
from email.message import EmailMessage

MI_CORREO = "zerokhyt@gmail.com"
MI_CLAVE_16 = "gkllljgczgycrwkd"

def descargar(asunto):
    query = f"ytsearch1:{asunto} audio"
    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': 'cancion.%(ext)s',
        'noplaylist': True
    }
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(query, download=True)
            return ydl.prepare_filename(info)
    except: return None

def ejecutar():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(MI_CORREO, MI_CLAVE_16)
        mail.select("inbox")
        _, data = mail.search(None, 'UNSEEN')
        for num in data[0].split():
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            asunto = msg["Subject"]
            print(f"🎵 Procesando: {asunto}")
            archivo = descargar(asunto)
            if archivo:
                # Lógica de envío (la misma que ya tienes)
                print(f"✅ Enviando {archivo}")
                os.remove(archivo)
            mail.store(num, '+FLAGS', '\\Seen')
        mail.logout()
    except Exception as e: print(f"Esperando... {e}")

if __name__ == "__main__":
    while True:
        ejecutar()
        time.sleep(10)