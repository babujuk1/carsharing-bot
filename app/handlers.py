from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import Message
from app import config, database

from aiogram import Bot , Dispatcher

bot = Bot(token = config.BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет , отправь мне сообщение и я перешлю его админам!")


@dp.message(F.chat.type=='private')
async def handle_message(message: Message):
    user_id = message.from_user.id
    wait_time = await database.check_rate_limit(user_id)

    if wait_time > 0:
        await message.answer(f"Пожалуйста, подождите {wait_time} секунд перед отправкой следующего сообщения.")
    else:
        await database.update_last_message_time(user_id)
        
        user = message.from_user
        if user.username:
            user_mention = f"@{user.username}"
        else:
            user_mention = f"{user.full_name} (ID: {user.id})"
        for admin_id in config.ADMIN_ID:
            try:
                if message.photo:
                    photo_id = message.photo[-1].file_id
                    caption = f"Сообщение от {user_mention}:"
                    await bot.send_photo(chat_id=admin_id, photo=photo_id, caption=caption)
                elif message.text:
                    await bot.send_message(chat_id=admin_id, text=user.mention + ": " + message.text)
                elif message.video_note:
                    await bot.send_message(chat_id=admin_id, text=user_mention)
                    await bot.send_video_note(chat_id=admin_id, video_note=message.video_note.file_id)
                elif message.voice:
                    await bot.send_voice(chat_id=admin_id, voice=message.voice.file_id, caption=user_mention)
                elif message.video:
                    await bot.send_video(chat_id=admin_id, video=message.video.file_id, caption=user_mention)
                else:
                    await bot.send_message(chat_id=admin_id, text=user_mention)

            except Exception as e:
                print(f"Ошибка при отправке админу {admin_id}: {e}")

            


