import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "7468967312:AAGeEoeJaD1WarTcLhbRBmbil1kD-Mz3khE"

logging.basicConfig(level=logging.INFO)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("تحميل فيديو", callback_data="download_video")],
        [InlineKeyboardButton("تحميل صوت", callback_data="download_audio")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("أهلاً بك! اختر ما تريد:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == "download_video":
        user_data[user_id] = "video"
        await query.edit_message_text("✅ أرسل رابط الفيديو للتحميل.")
    elif query.data == "download_audio":
        user_data[user_id] = "audio"
        await query.edit_message_text("✅ أرسل رابط الفيديو لاستخراج الصوت.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("❌ استخدم /start أولاً.")
        return

    choice = user_data[user_id]
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
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_document(document=open(filename, "rb"))
        os.remove(filename)  # حذف الملف بعد الإرسال لتوفير مساحة
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

    user_data.pop(user_id, None)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
