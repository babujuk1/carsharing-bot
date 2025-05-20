import asyncio
from app.handlers import dp , bot
from app.logger import logging
from app.database import close_connection



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
        logging.info('Бот запущен')
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
    finally:
        close_connection() 


    