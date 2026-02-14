from aiohttp import web_exceptions as exc
from aiohttp_session import get_session


class AuthRequiredMixin:
    async def _iter(self):
        session = await get_session(self.request)
        if "id" not in session:
            raise exc.HTTPUnauthorized(
                reason="Предоставьте действительную сессию для доступа к этому ресурсу"
            )
        self.request["id"] = session["id"]
        self.request["email"] = session["email"]
        return await super()._iter()
