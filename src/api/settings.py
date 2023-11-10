import os
import shutil
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import templates
from src.database import database
from src.dataclasses.settings import Settings
from src.utils.auth import get_current_user
from src.utils.common import get_default_question_years, get_hash, get_static_hash, get_word_form, save_image

router = APIRouter()


@router.get("/settings")
def get_settings(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/settings")

    template = templates.get_template("settings.html")
    settings = Settings.from_dict(database.settings.find_one({"username": user["username"]}))
    films_count = database.films.count_documents(settings.to_query())

    content = template.render(
        user=user,
        settings=settings,
        page="settings",
        version=get_static_hash(),
        have_statistic=database.statistic.find_one({"username": user["username"]}) is not None,
        question_years=get_default_question_years(),
        films_count=f'{films_count} {get_word_form(films_count, ["фильмов", "фильма", "фильм"])}',
        questions=constants.QUESTIONS,
        question2rus=constants.QUESTION_TO_RUS,
        productions=constants.PRODUCTIONS,
        production2rus=constants.PRODUCTION_TO_RUS,
        movie_types=constants.MOVIE_TYPES,
        movie_type2rus=constants.MOVIE_TYPE_TO_RUS,
        top_lists=constants.TOP_LISTS,
        top_list2rus=constants.TOP_LIST_TO_RUS
    )

    return HTMLResponse(content=content)


@router.post("/update-avatar")
async def update_avatar(image: UploadFile = File(...), user: Optional[dict] = Depends(get_current_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = save_image(image, tmp_dir)
        target_path = os.path.join("..", "plush-anvil", "web", "images", "profiles", f'{user["username"]}.jpg')
        shutil.move(file_path, target_path)
        image_hash = get_hash(target_path)

    database.users.update_one({"username": user["username"]}, {"$set": {"image_src": f'/profile-images/{user["username"]}.jpg?v={image_hash}'}}, upsert=True)
    return JSONResponse({"status": "success"})


@router.post("/update-settings")
async def update_settings(request: Request, user: Optional[dict] = Depends(get_current_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    data = await request.json()
    settings = Settings.from_dict(data)
    current_settings = Settings.from_dict(database.settings.find_one({"username": user["username"]}))

    if set(settings.questions) != set(current_settings.questions):
        settings.last_update = datetime.now()

    database.users.update_one({"username": user["username"]}, {"$set": {"fullname": data["fullname"]}})
    database.settings.update_one({"username": user["username"]}, {"$set": settings.to_dict()}, upsert=True)

    films_count = database.films.count_documents(settings.to_query())
    return JSONResponse({"status": "success", "films_count": films_count})
