from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pytube import YouTube
import yt_dlp
import os
import re
from dotenv import load_dotenv
load_dotenv()

def sanitize_filename(filename):
    return re.sub(r'[\/:*?"<>|]', '', filename)

def descargar_y_enviar_mp3(update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username
    url = context.args[0] if context.args else None

    if url:
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and 'formats' in info and info['formats']:
                    video_url = info['formats'][0]['url']
                    yt = YouTube(video_url)
                    stream = yt.streams.filter(only_audio=True).first()
                    if stream:
                        download_path = "downloads"
                        if not os.path.exists(download_path):
                            os.makedirs(download_path)

                        mp3_file = f"{sanitize_filename(yt.title)}.mp3"
                        stream.download(output_path=download_path, filename=mp3_file)
                        audio_file_path = os.path.join(download_path, mp3_file)
                        context.bot.send_audio(chat_id=user_id, audio=open(audio_file_path, 'rb'), title=yt.title)
                    else:
                        context.bot.send_message(chat_id=user_id, text="No se pudo obtener el stream de audio.")
                else:
                    context.bot.send_message(chat_id=user_id, text="No se pudo obtener la URL del video.")
        except Exception as e:
            context.bot.send_message(chat_id=user_id, text=f"Error: {str(e)}")
    else:
        context.bot.send_message(chat_id=user_id, text="Por favor, proporciona una URL válida.")

def unknown(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Hola! Probá con /mp3 [URL]")

def main():
    updater = Updater(os.getenv("TELEGRAM_KEY"), use_context=True)  
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("mp3", descargar_y_enviar_mp3, pass_args=True))
    dp.add_handler(MessageHandler(Filters.command, unknown))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
