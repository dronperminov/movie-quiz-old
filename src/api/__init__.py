import os
from typing import Optional

from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from src import constants

templates = Environment(loader=FileSystemLoader("web/templates"), cache_size=0)

with open(os.path.join(os.path.dirname(__file__), "..", "..", "tokens.txt"), "r") as f:
    tokens = f.read().splitlines()


def make_error(message: str, user: Optional[dict], title: str = "Произошла ошибка") -> HTMLResponse:
    template = templates.get_template("error.html")
    content = template.render(user=user, page="error", title=title, message=message, version=constants.VERSION)
    return HTMLResponse(content=content)
