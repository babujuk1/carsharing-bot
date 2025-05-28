from typing import Dict, List, Any, Callable, Awaitable
import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message

class AlbumMiddleware(BaseMiddleware):

    def __init__(self, wait_time: float = 1.0):

        self.wait_time = wait_time
        self.albums: Dict[str, List[Message]] = {}
        self.lock = asyncio.Lock()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        if not event.media_group_id:
            return await handler(event, data)


        async with self.lock:
            self.albums.setdefault(event.media_group_id, []).append(event)


        await asyncio.sleep(self.wait_time)


        async with self.lock:
            if event.media_group_id in self.albums:
                messages = self.albums[event.media_group_id]
                if len(messages) > 0 and messages[-1].message_id == event.message_id:

                    data["album"] = messages


                    print(f"Медиа-группа {event.media_group_id} собрана полностью, {len(messages)} сообщений")


                    for msg in messages:
                        if msg.caption:
                            print(f"Сообщение {msg.message_id} содержит подпись: {msg.caption}")


                    del self.albums[event.media_group_id]

                    return await handler(event, data)


        return None
