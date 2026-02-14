import typing

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor
from app.web.utils import hash_password

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        await self.create_admin(
            email=self.app.config.admin.email,
            password=hash_password(self.app.config.admin.password),
        )

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = Admin(
            id=self.app.database.next_admin_id, email=email, password=password
        )
        self.app.database.admins.append(admin)
        return admin
