import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from deepface import DeepFace
import uuid

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# پیام خوش‌آمد و راهنمای عکاسی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من **رویا بات** هستم. با ارسال یک عکس واضح از چهره‌ات، شخصیت، احساس و ویژگی‌هات رو تحلیل می‌کنم!\n\n"
        "قبل از ارسال عکس لطفاً این موارد رو رعایت کن:\n"
        "- نور خوب (ترجیحاً نور طبیعی)\n"
        "- صورت کامل و مستقیم به دوربین\n"
        "- بدون فیلتر یا افکت\n"
        "- بدون عینک آفتابی یا ماسک\n\n"
        "حالا یه عکس بفرست..."
    )

# تحلیل عکس
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = f\"/tmp/{uuid.uuid4()}.jpg\"
    await file.download_to_drive(file_path)

    try:
        result = DeepFace.analyze(img_path=file_path, actions=['emotion', 'age', 'gender'], enforce_detection=False)[0]
        os.remove(file_path)

        response = (
            f"**نتیجه تحلیل چهره:**\n"
            f"- جنسیت: {result['gender']}\n"
            f"- سن تخمینی: {result['age']}\n"
            f"- احساس غالب: {result['dominant_emotion']}\n\n"
            f"برای تحلیل کامل‌تر فرم چهره، شخصیت‌شناسی سنتی و مشاوره روحی، نسخه VIP رو فعال کن."
        )
    except:
        response = "نتونستم عکس رو تحلیل کنم. لطفاً یه عکس واضح‌تر بفرست."

    await update.message.reply_text(response)

if __name__ == '__main__':
    TOKEN = os.getenv(\"7443958941:AAFOME7UaMsQTzvZhrWFTd6UF0bPceCAk4E\")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler(\"start\", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
