import random
from typing import Optional

import yandex_music.exceptions
from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from src.api import yandex_tokens
from src.utils.audio import get_track_ids, parse_direct_link, parse_tracks
from src.utils.auth import get_current_user

router = APIRouter()


@router.post("/parse-audios")
def parse_audios(user: Optional[dict] = Depends(get_current_user), code: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    track_ids = get_track_ids(code, random.choice(yandex_tokens))

    if not track_ids:
        return JSONResponse({"status": "error", "message": "Не удалось распарсить ни одного аудио"})

    tracks = parse_tracks(track_ids, random.choice(yandex_tokens), True)
    return JSONResponse({"status": "success", "tracks": tracks})


@router.post("/get-direct-link")
def get_direct_link(user: Optional[dict] = Depends(get_current_user), track_id: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    try:
        direct_link = parse_direct_link(track_id, random.choice(yandex_tokens))
    except yandex_music.exceptions.BadRequestError:
        return JSONResponse({"status": "error", "message": "Не удалось получить ссылку на аудио"})

    return JSONResponse({"status": "success", "direct_link": direct_link})
