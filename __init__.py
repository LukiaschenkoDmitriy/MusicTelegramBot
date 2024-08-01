from dotenv import load_dotenv
import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters, MessageHandler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


USERS_FILES = {

}

keyboard = [
    ['Змінити назву', "Змінити виконавця"],
    ['Змінити теги', 'Змінити обкладинку'],
    ["Показати результат"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привіт {update.effective_user.first_name}')
    await update.message.reply_text("Я бот для редагування музичних даних у Telegram. У мене є наступний функціонал: Змінювати назву музики, додавати фото до музики, додавати теги.")
    await update.message.reply_text("Для того, щоб почати працювати зі мною, ви повинні надіслати мені аудіофайл, надішліть мені свій аудіофайл.")


async def audio_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    audio_file = update.message.audio
    if audio_file:

        audio_file_id = audio_file.file_id

        await update.message.reply_text(f"Аудіофайл завантажується...")

        file = await context.bot.get_file(audio_file_id, read_timeout=30, write_timeout=30)

        await file.download_to_drive(f"./{audio_file_id}")

        USERS_FILES[update.message.from_user.id] = {
            "file_id": audio_file_id,
            "title": None,
            "cover_id": None,
            "performer": None,
            "tags": [],
            "state": None
        }

        await update.message.reply_text(f"Аудіофайл успішно загружено.")
        await update.message.reply_text(f"Що ви хочете зробити з аудіофайлом?", reply_markup=reply_markup)

async def change_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (update.message.from_user.id in USERS_FILES):
        await update.message.reply_text("Введіть заголовок аудіофайла.")
        USERS_FILES[update.message.from_user.id]["state"] = "EDIT_TITLE"
    else:
        await update.message.reply_text("Для початку загрузіть свій аудіофайл.")

async def change_performer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (update.message.from_user.id in USERS_FILES):
        await update.message.reply_text("Введіть виконавця аудіофайла.")
        USERS_FILES[update.message.from_user.id]["state"] = "EDIT_PERFORMER"
    else:
        await update.message.reply_text("Для початку загрузіть свій аудіофайл.")

async def change_cover(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (update.message.from_user.id in USERS_FILES):
        await update.message.reply_text("Надішліть обкладинку.")
        USERS_FILES[update.message.from_user.id]["state"] = "EDIT_COVER"
    else:
        await update.message.reply_text("Для початку загрузіть свій аудіофайл.")

async def change_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Ви обрали зміну тегів музики.")

async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id in USERS_FILES:
        with open(f"./{USERS_FILES[update.message.from_user.id]['file_id']}", 'rb') as audio_file:
            if os.path.exists(f"./cover/{USERS_FILES[update.message.from_user.id]['cover_id']}"):
                with open(f"./cover/{USERS_FILES[update.message.from_user.id]['cover_id']}", 'rb') as cover_file:
                    await context.bot.send_audio(
                        chat_id=update.effective_user.id, 
                        audio=audio_file, 
                        title=USERS_FILES[update.message.from_user.id]['title'], 
                        performer=USERS_FILES[update.message.from_user.id]['performer'],
                        thumbnail=cover_file,
                        reply_markup=reply_markup)
            await context.bot.send_audio(
                        chat_id=update.effective_user.id, 
                        audio=audio_file, 
                        title=USERS_FILES[update.message.from_user.id]['title'], 
                        performer=USERS_FILES[update.message.from_user.id]['performer'],
                        reply_markup=reply_markup)
    else:
        await update.message.reply_text("Для початку загрузіть свій аудіофайл.")

async def update_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (USERS_FILES[update.message.from_user.id]["state"] == "EDIT_TITLE"):
        USERS_FILES[update.message.from_user.id]["title"] = update.message.text
        await update.message.reply_text("Назва аудіофайла змінена успішно.", reply_markup=reply_markup, read_timeout=30, write_timeout=30)

        USERS_FILES[update.message.from_user.id]["state"] = None

    elif (USERS_FILES[update.message.from_user.id]["state"] == "EDIT_PERFORMER"):
        USERS_FILES[update.message.from_user.id]["performer"] = update.message.text
        await update.message.reply_text("Виконавець аудіофайла змінений успішно.", reply_markup=reply_markup)

        USERS_FILES[update.message.from_user.id]["state"] = None

async def update_cover(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (USERS_FILES[update.message.from_user.id]["state"] == "EDIT_COVER"):
        photo = update.message.photo[-1]
        cover_file_id = photo.file_id

        file = await context.bot.get_file(cover_file_id, read_timeout=30, write_timeout=30 )

        await file.download_to_drive(f"./cover/{cover_file_id}")

        USERS_FILES[update.message.from_user.id]["cover_id"] = cover_file_id
        await update.message.reply_text("Обкладинка змінена успішно.", reply_markup=reply_markup)

        USERS_FILES[update.message.from_user.id]["state"] = None




app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.AUDIO, audio_file))
app.add_handler(MessageHandler(filters.PHOTO, update_cover))

app.add_handler(MessageHandler(filters.Regex('Змінити назву'), change_title))
app.add_handler(MessageHandler(filters.Regex('Змінити обкладинку'), change_cover))
app.add_handler(MessageHandler(filters.Regex('Змінити теги'), change_tags))
app.add_handler(MessageHandler(filters.Regex('Змінити виконавця'), change_performer))
app.add_handler(MessageHandler(filters.Regex('Показати результат'), preview))

app.add_handler(MessageHandler(filters.TEXT, update_data))


app.run_polling()