# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import os
import yt_dlp

TOKEN = "7468967312:AAGeEoeJaD1WarTcLhbRBmbil1kD-Mz3khE"
USER_DATA = {}

# ---------------- downloader ----------------
def download_media(url, folder="downloads", audio_only=False):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    ydl_opts = {}
    if audio_only:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    info_dict = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
    title = info_dict.get('title', 'video')
    ext = 'mp3' if audio_only else 'mp4'
    return f"{folder}/{title}.{ext}"

# ---------------- بوت تيليجرام ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً! أرسل لي رابط الفيديو أو الصوت لأقوم بالتحميل.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url:
        await update.message.reply_text("❌ الرجاء إرسال رابط صحيح.")
        return

    USER_DATA[update.effective_user.id] = url
    keyboard = [
        [InlineKeyboardButton("تحميل فيديو MP4", callback_data='video')],
        [InlineKeyboardButton("تحميل صوت MP3", callback_data='audio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = USER_DATA.get(query.from_user.id)
    if not url:
        await query.edit_message_text("❌ لم أرسل رابط بعد.")
        return

    await query.edit_message_text("⏳ جاري التحميل...")
    try:
        filepath = download_media(url, audio_only=(query.data=='audio'))
        with open(filepath, 'rb') as f:
            await context.bot.send_document(chat_id=query.from_user.id, document=f)
    except Exception as e:
        await context.bot.send_message(chat_id=query.from_user.id, text=f"❌ فشل التحميل: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
