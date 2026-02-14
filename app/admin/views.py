from aiohttp import web_exceptions as exc
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminResponseSchema, AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response, verify_password


class AdminLoginView(View):
    @docs(tags=["Admin"], summary="Вход администратора", description="Вход администратора по email и паролю")
    @request_schema(AdminSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        data = self.request["data"]
        admin = await self.store.admins.get_by_email(email=data["email"])
        if not admin or not verify_password(password=data["password"], hashed_password=admin.password):
            self.store.admins.logger.warning("Не верная попытка входа.")
            raise exc.HTTPForbidden(reason="Неверный email или пароль")
        session = await new_session(self.request)
        session["email"] = admin.email
        session["id"] = admin.id
        return json_response(data=AdminResponseSchema().dump(admin))


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=["Admin"],
        summary="Текущий профиль",
        description="Получить текущий профиль администратора, используя данные из сессии",
    )
    @response_schema(OkResponseSchema, 200)
    async def get(self):
        admin = await self.store.admins.get_by_email(
            email=self.request["email"]
        )
        return json_response(data=AdminResponseSchema().dump(admin))
