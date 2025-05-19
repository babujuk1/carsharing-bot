from aiogram import Bot , Dispatcher 
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
from aiogram import F
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")



bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)



@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет , отправь мне сообщение и я перешлю его админам!")

@dp.message(F.chat.type=='private')
async def handle_message(message: Message):
    await bot.send_message(chat_id=CHAT_ID,text=f"Сообщение от @{message.from_user.username}: {message.text}")
    await message.answer("Ваше сообщение отправлено администратору!")
    


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        print(e)

        
    

    