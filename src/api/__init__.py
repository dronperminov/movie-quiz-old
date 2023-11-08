import os
from typing import Optional

from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from src.database import database
from src.utils.common import get_static_hash
from src.utils.kinopoisk_api import KinopoiskAPI

templates = Environment(loader=FileSystemLoader("web/templates"), cache_size=0)

with open(os.path.join(os.path.dirname(__file__), "..", "..", "tokens.txt"), "r") as f:
    kinopoisk_api = KinopoiskAPI(f.read().splitlines())

with open(os.path.join(os.path.dirname(__file__), "..", "..", "yandex_tokens.txt"), "r") as f:
    yandex_tokens = f.read().splitlines()


def make_error(message: str, user: Optional[dict], title: str = "Произошла ошибка") -> HTMLResponse:
    template = templates.get_template("error.html")
    settings = database.settings.find_one({"username": user["username"]}) if user else None
    content = template.render(user=user, settings=settings, page="error", title=title, message=message, version=get_static_hash())
    return HTMLResponse(content=content)
