import asyncio
from app.handlers import dp , bot
from app.database import close_connection



async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await close_connection()


if __name__ == '__main__':
    try:
        asyncio.run(main())
        print("Бот запущен")
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


    