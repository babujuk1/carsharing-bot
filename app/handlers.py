from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import Message
from app import config, database, logging

from aiogram import Bot , Dispatcher

bot = Bot(token = config.BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет , отправь мне сообщение и я перешлю его админам!")


@dp.message(F.chat.type=='private')
async def handle_message(message: Message):
    user_id = message.from_user.id
    wait_time = database.check_rate_limit(user_id)

    if wait_time > 0:
        await message.answer(f"Пожалуйста, подождите {wait_time} секунд перед отправкой следующего сообщения.")
    else:
        database.update_last_message_time(user_id)
        user_info = f"Сообщение от пользователя {message.from_user.full_name}: {message.text}"
        if message.photo:
            photo_id = message.photo[-1].file_id
            caption = message.caption if message.caption else ""
            await bot.send_photo(chat_id=config.CHAT_ID,photo=photo_id,caption=caption)
            logging.info(f'Отправлено фото от {message.from_user.full_name}')
        elif message.text:
            text = message.text
            await bot.send_message(chat_id=config.CHAT_ID, text=text)
            logging.info(f'Отправлен текст от {message.from_user.full_name}')
        elif message.video_note:
            video_note_id = message.video_note.file_id
            await bot.send_video_note(chat_id=config.CHAT_ID, video_note=video_note_id)
            logging.info(f'Отправлен кружок от {message.from_user.full_name}')
        elif message.voice:
            voice_id = message.voice.file_id
            caption = message.caption if message.caption else ""
            await bot.send_voice(chat_id=config.CHAT_ID, voice=voice_id, caption=caption)
            logging.info(f'Отправлен гс от {message.from_user.full_name}')
        elif message.video:
            video_id = message.video.file_id
            caption = message.caption if message.caption else ""
            await bot.send_video(chat_id=config.CHAT_ID, video=video_id, caption=caption)
            logging.info(f'Отправлено видео от {message.from_user.full_name}')
        else:
            await message.answer("Неподдерживаемый формат сообщения.\n Вы можете отправить текст, фото, видео или голосовое сообщение.")
            logging.info(f'Неподдерживаемый формат сообщения от {message.from_user.full_name}')
