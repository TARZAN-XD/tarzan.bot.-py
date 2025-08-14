from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from downloader import download_media

TOKEN = "7468967312:AAGeEoeJaD1WarTcLhbRBmbil1kD-Mz3khE"
USER_DATA = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً! أرسل لي رابط الفيديو لأقوم بتحميله.")

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
    user_id = query.from_user.id
    await query.answer()
    
    url = USER_DATA.get(user_id)
    if not url:
        await query.edit_message_text("❌ لم أجد رابط. أرسل رابط الفيديو أولاً.")
        return

    await query.edit_message_text("⏳ جاري التحميل...")
    
    try:
        if query.data == 'video':
            filepath = download_media(url, audio_only=False)
        else:
            filepath = download_media(url, audio_only=True)
        
        with open(filepath, 'rb') as f:
            await context.bot.send_document(chat_id=user_id, document=f)
    except Exception as e:
        await context.bot.send_message(chat_id=user_id, text=f"❌ فشل التحميل: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == "__main__":
    main()
