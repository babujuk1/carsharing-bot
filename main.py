from aiogram import Bot , Dispatcher 
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
from aiogram import F, Dispatcher, Bot
import time
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")



bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_messages (
        user_id INTEGER PRIMARY KEY,
        last_message_time REAL
    )
''')
conn.commit()


async def check_rate_limit(user_id):
    cursor.execute("SELECT last_message_time FROM user_messages WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        last_message_time = result[0]
        time_limit = 20  
        if time.time() - last_message_time < time_limit:
            return int(time_limit - (time.time() - last_message_time))
    return 0


async def update_last_message_time(user_id):
    cursor.execute("INSERT OR REPLACE INTO user_messages (user_id, last_message_time) VALUES (?, ?)", (user_id, time.time()))
    conn.commit()



@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет , отправь мне сообщение и я перешлю его админам!")


@dp.message(F.chat.type=='private')
async def handle_message(message: Message):
    user_id = message.from_user.id
    wait_time = await check_rate_limit(user_id)

    if wait_time > 0:
        await message.answer(f"Пожалуйста, подождите {wait_time} секунд перед отправкой следующего сообщения.")
    else:
        await update_last_message_time(user_id)
        user_info = f"Сообщение от пользователя {message.from_user.full_name}: {message.text}"
        if message.photo:
            photo_id = message.photo[-1].file_id
            caption = message.caption if message.caption else ""
            await bot.send_photo(chat_id=CHAT_ID,photo=photo_id,caption=caption)
        elif message.text:
            text = message.text
            await bot.send_message(chat_id=CHAT_ID, text=text)
        elif message.video:
            video_id = message.video.file_id
            caption = message.caption if message.caption else ""
            await bot.send_video(chat_id=CHAT_ID, video=video_id, caption=caption)



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
    finally:
        conn.close()  


    