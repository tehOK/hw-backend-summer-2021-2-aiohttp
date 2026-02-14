import typing
from asyncio.exceptions import TimeoutError
from urllib.parse import urlencode, urljoin

from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ClientError

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import (
    Message,
    Update,
    UpdateMessage,
    UpdateObject,
)
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.199"
VK_API_BASE_URL = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None
        self.token: str | None = self.app.config.bot.token
        self.group_id: int | None = self.app.config.bot.group_id

    async def connect(self, app: "Application") -> None:
        self.session = ClientSession()
        await self._get_long_poll_service()
        self.poller = Poller(self.app.store)
        await self.poller.start()
        self.logger.info("VkApiAccessor connected")

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()
        self.logger.info("VkApiAccessor disconnected")

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        params = {
            "group_id": self.group_id,
            "access_token": self.token,
        }
        url = self._build_query(
            host=VK_API_BASE_URL,
            method="groups.getLongPollServer",
            params=params,
        )
        async with self.session.get(url) as resp:
            data = await resp.json()
            response = data.get("response")
            self.key = response["key"]
            self.server = response["server"]
            self.ts = int(response["ts"])
            return

    async def poll(self):
        params = {
            "key": self.key,
            "ts": self.ts,
            "wait": 25,
            "mode": 2,
            "version": API_VERSION,
        }
        try:
            async with self.session.get(self.server, params=params) as response:
                if response.status != 200:
                    self.logger.error(
                        "VK api вернул код ответа: %s", response.status
                    )
                    return []

                data = await response.json()

                if "error" in data:
                    self.logger.error("VK api error: %s", data["error"])
                    return []

                if "ts" in data:
                    self.ts = data["ts"]

                updates = []
                if "updates" in data:
                    for update_data in data["updates"]:
                        if update_data.get("type") == "message_new":
                            message_data = update_data.get("object", {}).get(
                                "message", {}
                            )
                            update_message = UpdateMessage(
                                from_id=message_data.get("from_id"),
                                text=message_data.get("text"),
                                id=message_data.get("id"),
                            )
                            update_object = UpdateObject(message=update_message)
                            update = Update(
                                type=update_data["type"], object=update_object
                            )
                            updates.append(update)
                return updates

        except TimeoutError:
            self.logger.error("Poll operation timed out")
            return []

        except ClientError as e:
            self.logger.error("Client error %s", e)
            return []

        except Exception as e:
            self.logger.error("Unexpected error %s", e)
            return []

    async def send_message(self, message: Message) -> None:
        params = {
            "user_id": message.user_id,
            "message": message.text,
            "access_token": self.token,
            "v": API_VERSION,
            "random_id": 0,
        }
        url = self._build_query(
            host=VK_API_BASE_URL,
            method="messages.send",
            params=params,
        )
        async with self.session.get(url) as resp:
            await resp.json()
