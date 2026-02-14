import typing

from aiohttp_session import setup as setup_aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography.fernet import Fernet

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_session(app: "Application") -> None:
    key = app.config.session.key.encode()
    fernet = Fernet(key)
    setup_aiohttp_session(app, EncryptedCookieStorage(fernet))
