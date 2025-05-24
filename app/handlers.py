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

        if message.photo:
            photo_id = message.photo[-1].file_id
            original_caption = message.caption or ""
            forward_content = f"От {user_mention}:\n{original_caption}".strip()
            
            
        elif message.text:
            forward_content = f"От {user_mention}:\n{message.text}"
            

        elif message.video_note:
            forward_content = message.video_note.file_id
            
            
        elif message.voice:
            voice_id = message.voice.file_id
            original_caption = message.caption or ""
            forward_caption = f"От {user_mention}:\n{original_caption}".strip()
            

        elif message.video:
            video_id = message.video.file_id
            original_caption = message.caption or ""
            forward_caption = f"От {user_mention}:\n{original_caption}".strip()
            
            
        else:
            forward_content=f"Неподдерживаемый формат сообщения❌.\n Вы можете отправить текст, фото, видео или голосовое сообщение."
        for admin_id in config.ADMIN_ID:
            try:
                if message.photo:  # Если сообщение содержит фото
                    await bot.send_photo(chat_id=admin_id, photo=photo_id, caption=forward_content)
                elif message.text:  # Если сообщение содержит текст
                    await bot.send_message(chat_id=admin_id, text=forward_content)
                elif message.video_note:  # Если сообщение содержит видео-кружок
                    await bot.send_message(chat_id=admin_id, text=forward_content)
                    await bot.send_video_note(chat_id=admin_id, video_note=message.video_note.file_id)
                elif message.voice:  # Если сообщение содержит голосовое сообщение
                    await bot.send_voice(chat_id=admin_id, voice=message.voice.file_id, caption=forward_content)
                elif message.video:  # Если сообщение содержит видео
                    await bot.send_video(chat_id=admin_id, video=message.video.file_id, caption=forward_content)
                else:
                    await bot.send_message(chat_id=admin_id, text=forward_content)

            except Exception as e:
                print(f"Ошибка при отправке админу {admin_id}: {e}")
