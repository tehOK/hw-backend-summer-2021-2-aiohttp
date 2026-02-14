import typing

from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

    async def handle_updates(self, updates: list[Update]) -> None:
        for update in updates:
            await self.handle_update(update=update)

    async def handle_update(self, update: Update) -> None:
        if update.type == "message_new":
            message = update.object.message
            response_message = Message(
                user_id=message.from_id,
                text=f"Привет, ты написал: {message.text}",
            )
            await self.app.store.vk_api.send_message(response_message)
