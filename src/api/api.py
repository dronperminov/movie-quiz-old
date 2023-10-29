from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from src import constants
from src.api import templates
from src.database import database
from src.utils.auth import get_current_user
from src.utils.statistic import get_statistic

router = APIRouter()


@router.get("/")
def index(user: Optional[dict] = Depends(get_current_user)) -> HTMLResponse:
    template = templates.get_template("index.html")

    usernames = database.statistic.distinct("username")
    statistics = dict()

    for username in usernames:
        statistics[username] = get_statistic(username)
        statistics[username]["image"] = database.users.find_one({"username": username}, {"image_src": 1})["image_src"]

    usernames = sorted(usernames, key=lambda username: -statistics[username]["questions"]["correct"])[:constants.TOP_COUNT]
    content = template.render(user=user, page="index", version=constants.VERSION, statistics=statistics, usernames=usernames)
    return HTMLResponse(content=content)
