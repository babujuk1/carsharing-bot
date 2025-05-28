from aiogram import F
from aiogram.filters import CommandStart , Command
from aiogram.types import Message , InputMediaVideo , InputMediaPhoto , InputMediaDocument
from app import config, database
from aiogram import Bot , Dispatcher
from app.middleware import AlbumMiddleware

bot = Bot(token = config.BOT_TOKEN)
dp = Dispatcher()


dp.message.middleware(AlbumMiddleware(wait_time=1.5))

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("1. Что ты хочешь отправить?\n"
                            "🔘 Новость о каршеринге\n"
                            "🔘 Личный случай / история\n"
                            "🔘 Фото / видео\n"
                            "🔘 Вопрос или идея для блога\n\n"
                            "2. Насколько это срочно?\n"
                         "🔘 Просто поделиться\n"
                         "🔘 Можно опубликовать сегодня\n"
                         "🔘 Это важно — может повлиять на других\n\n"
                         "3. Хочешь, чтобы мы указали тебя как автора?\n"
                         "🔘 Да, укажите свой @ник\n"
                         "🔘 Нет, пусть будет анонимно\n\n"
                         "Напишите сообщение ниже и админы его получат⬇️"
                         )

@dp.message(F.chat.type=='private',Command("send"))
async def send(message: Message):
    if str(message.from_user.id) not in config.ADMINS:
        await message.answer("У вас нет доступа к этой команде.")
        return

    commands_parts = message.text.split(maxsplit=2)
    if len(commands_parts) < 3:
        await message.answer("Надо так /send @username сообщение\n Ещё раз напиши команду")
    try:
        username = commands_parts[1]
        text = commands_parts[2]
        chat = await bot.get_chat(username)
        user_id = chat.id
        await bot.send_message(chat_id=user_id, text=text)
        await message.answer(f"Сообщение успешно отправлено пользователю: {username}.")
    except Exception as e:
        print(f"Ошибка при отправке пользователю {username}: {e}")
        await message.answer(
            f"Не удалось отправить сообщение пользователю {username}. Возможно, он не начинал диалог с ботом.")



@dp.message(F.chat.type=='private')
async def handle_message(message: Message, album=None):

    message_delivered = False
    user_id = message.from_user.id
    wait_time = await database.check_rate_limit(user_id)
    if wait_time > 0:
        await message.answer(f"Пожалуйста, подождите {wait_time} секунд перед отправкой следующего сообщения.")
    else:
        await database.update_last_message_time(user_id)
        
        user = message.from_user
        if user.username:
            user_mention = f"@{user.username} (ID: {user.id})"
        else:
            user_mention = f"{user.full_name} (ID: {user.id})"

        for admin in config.ADMINS:
            try:

                if album:
                    print(f"Обработка альбома, количество файлов: {len(album)}")
                    media = []


                    user_caption = ""
                    for msg in album:
                        if msg.caption:
                            user_caption = msg.caption
                            print(f"Найдена подпись: {user_caption}")
                            break

                    for i, msg in enumerate(album):

                        if i == 0:
                            if user_caption:
                                caption = f"Сообщение от {user_mention}:\n\n{user_caption}"
                            else:
                                caption = f"Сообщение от {user_mention}:"
                        else:
                            caption = None

                        if msg.photo:
                            media.append(InputMediaPhoto(
                                media=msg.photo[-1].file_id,
                                caption=caption
                            ))
                        elif msg.video:
                            media.append(InputMediaVideo(
                                media=msg.video.file_id,
                                caption=caption
                            ))
                        elif msg.document:
                            media.append(InputMediaDocument(
                                media=msg.document.file_id,
                                caption=caption
                            ))


                    print(f"Медиа для отправки: {len(media)} элементов")
                    if len(media) > 0 and media[0].caption:
                        print(f"Текст первого элемента: {media[0].caption}")


                    if media:
                        await bot.send_media_group(chat_id=admin, media=media)
                        message_delivered = True
                        print(f"Альбом успешно отправлен администратору {admin}")


                else:
                    if message.photo:
                        photo_id = message.photo[-1].file_id
                        caption = f"Сообщение от {user_mention}:"
                        await bot.send_photo(chat_id=admin, photo=photo_id, caption=caption)
                    elif message.text:
                        await bot.send_message(chat_id=admin, text=user_mention + ": " + message.text)
                        print("Обработан текст")
                    elif message.video_note:
                        await bot.send_message(chat_id=admin, text=user_mention)
                        await bot.send_video_note(chat_id=admin, video_note=message.video_note.file_id)
                    elif message.voice:
                        await bot.send_voice(chat_id=admin, voice=message.voice.file_id, caption=user_mention)
                    elif message.video:
                        await bot.send_video(chat_id=admin, video=message.video.file_id, caption=user_mention)
                    else:
                        await bot.send_message(chat_id=admin, text=user_mention)

                    message_delivered = True


            except Exception as e:
                print(f"Ошибка при отправке админу {admin}: {e}")


        if message_delivered:
            if not album or (album and message.message_id == album[-1].message_id):
                await message.answer("Сообщение успешно отправлено✅.")
        else:
            print("Сообщение не доставлено")

            


