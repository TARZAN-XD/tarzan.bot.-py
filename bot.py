from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from downloader import download_media

TOKEN = "7468967312:AAGeEoeJaD1WarTcLhbRBmbil1kD-Mz3khE"
USER_DATA = {}  # لتخزين الرابط المؤقت لكل مستخدم

def start(update: Update, context: CallbackContext):
    update.message.reply_text("أهلاً! أرسل لي رابط الفيديو لأقوم بتحميله.")

def handle_link(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    if not url:
        update.message.reply_text("❌ الرجاء إرسال رابط صحيح.")
        return
    
    USER_DATA[update.effective_user.id] = url
    keyboard = [
        [InlineKeyboardButton("تحميل فيديو MP4", callback_data='video')],
        [InlineKeyboardButton("تحميل صوت MP3", callback_data='audio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    
    url = USER_DATA.get(user_id)
    if not url:
        query.edit_message_text("❌ لم أجد رابط. أرسل رابط الفيديو أولاً.")
        return

    query.edit_message_text("⏳ جاري التحميل...")
    
    try:
        if query.data == 'video':
            filepath = download_media(url, audio_only=False)
        else:
            filepath = download_media(url, audio_only=True)
        
        with open(filepath, 'rb') as f:
            context.bot.send_document(chat_id=user_id, document=f)
    except Exception as e:
        context.bot.send_message(chat_id=user_id, text=f"❌ فشل التحميل: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
