import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "7468967312:AAGeEoeJaD1WarTcLhbRBmbil1kD-Mz3khE"

logging.basicConfig(level=logging.INFO)
user_data = {}

# بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("تحميل فيديو", callback_data="video")],
        [InlineKeyboardButton("تحميل صوت", callback_data="audio")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر ما تريد:", reply_markup=reply_markup)

# التعامل مع الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id] = query.data
    await query.edit_message_text(f"✅ أرسل الرابط الآن لتحميل {query.data}")

# التعامل مع الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("❌ استخدم /start أولاً")
        return

    choice = user_data[user_id]
    url = update.message.text
    await update.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {}
    if choice == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{user_id}_%(title)s.%(ext)s',
            'noplaylist': True,
        }
    else:
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{user_id}_%(title)s.%(ext)s',
            'noplaylist': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_document(open(filename, "rb"))
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

    user_data.pop(user_id, None)

# تهيئة وتشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
