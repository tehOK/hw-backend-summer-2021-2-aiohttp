from asyncio import Task

from app.store import Store


class Poller:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None

    async def start(self) -> None:
        self.is_running = True
        self.poll_task = Task(self.poll())

    async def stop(self) -> None:
        if self.poll_task:
            self.poll_task.cancel()
        self.is_running = False

    async def poll(self) -> None:
        while self.is_running:
            try:
                updates = await self.store.vk_api.poll()
                if updates:
                    await self.store.bots_manager.handle_updates(
                        updates=updates
                    )
            except Exception as e:
                self.store.logger.error("Ошибка при опросе: %s", e)
