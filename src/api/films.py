import os
import random
import tempfile
from typing import List, Optional
from urllib.error import HTTPError, URLError

import wget
import yandex_music.exceptions
from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates, yandex_tokens
from src.database import database
from src.dataclasses.film_form import FilmForm
from src.dataclasses.films_query import FilmsQuery
from src.utils.audio import get_track_ids, parse_direct_link, parse_tracks
from src.utils.auth import get_current_user
from src.utils.common import get_hash, get_static_hash, get_word_form, resize_preview
from src.utils.film import add_cites, get_films_by_ids, get_images_by_ids, preprocess_film

router = APIRouter()


@router.get("/films")
def get_films(user: Optional[dict] = Depends(get_current_user), search_params: FilmsQuery = Depends()) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/films")

    if search_params.is_empty():
        return RedirectResponse(url="/films")

    settings = database.settings.find_one({"username": user["username"]})
    query = search_params.to_query()
    films = list(database.films.find(query).sort("name", 1)) if query else []

    if search_params.top_lists:
        films = sorted(films, key=lambda film: min(position for top_name, position in film["topPositions"].items() if top_name in search_params.top_lists))

    total_films = database.films.count_documents({})
    query_correspond_form = get_word_form(len(films), ["запросу соответствуют", "запросу соответствуют", "запросу соответствует"])
    query_films_form = get_word_form(len(films), ["фильмов", "фильма", "фильм"])
    total_correspond_form = get_word_form(total_films, ["находятся", "находятся", "находится"])
    total_films_form = get_word_form(total_films, ["фильмов", "фильма", "фильм"])

    template = templates.get_template("films/films.html")
    content = template.render(
        user=user,
        settings=settings,
        page="films",
        version=get_static_hash(),
        films=films,
        total_films=f"{total_correspond_form} {total_films} {total_films_form}",
        query_films=f"{query_correspond_form} {len(films)} {query_films_form}",
        query=search_params.query if search_params.query else "",
        search_start_year=search_params.start_year if search_params.start_year else "",
        search_end_year=search_params.end_year if search_params.end_year else "",
        search_movie_types=search_params.movie_types if search_params.movie_types else [],
        search_top_lists=search_params.top_lists if search_params.top_lists else [],
        search_productions=search_params.production if search_params.production else [],
        movie_types=constants.MOVIE_TYPES,
        movie_type2rus=constants.MOVIE_TYPE_TO_RUS,
        top_lists=constants.TOP_LISTS,
        top_list2rus=constants.TOP_LIST_TO_RUS,
        productions=constants.PRODUCTIONS,
        production2rus=constants.PRODUCTION_TO_RUS
    )
    return HTMLResponse(content=content)


@router.get("/films/{film_id}")
def get_film(film_id: int, user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url=f"/login?back_url=/films/{film_id}")

    film = database.films.find_one({"film_id": film_id})

    if not film:
        return make_error(message="Запрашиваемого фильма не существует", user=user)

    settings = database.settings.find_one({"username": user["username"]})
    template = templates.get_template("films/film.html")
    content = template.render(
        user=user,
        settings=settings,
        page="film",
        version=get_static_hash(),
        film=film,
        movie_types=constants.MOVIE_TYPES,
        movie_type2rus=constants.MOVIE_TYPE_TO_RUS,
        top_lists=constants.TOP_LISTS,
        top_list2rus=constants.TOP_LIST_TO_RUS
    )
    return HTMLResponse(content=content)


@router.get("/add-films")
def get_add_films(user: Optional[dict] = Depends(get_current_user)) -> Response:
    if not user:
        return RedirectResponse(url="/login?back_url=/add-films")

    settings = database.settings.find_one({"username": user["username"]})
    template = templates.get_template("films/add_film.html")
    content = template.render(user=user, settings=settings, page="add-films", version=get_static_hash())
    return HTMLResponse(content=content)


@router.post("/parse-films")
def parse_films(user: Optional[dict] = Depends(get_current_user), film_ids: List[int] = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    existed_film_ids = {film["film_id"] for film in database.films.find({"film_id": {"$in": film_ids}})}
    film_ids = [film_id for film_id in film_ids if film_id not in existed_film_ids]
    parsed_films = get_films_by_ids(film_ids)

    films = []
    for parsed_film in parsed_films:
        if film := preprocess_film(parsed_film):
            films.append(film)

    add_cites(films)
    return JSONResponse({"status": "success", "films": films})


@router.post("/add-films")
def add_films(user: Optional[dict] = Depends(get_current_user), films: List[dict] = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    existed_film_ids = {film["film_id"] for film in database.films.find({})}
    films = [film for film in films if film["film_id"] not in existed_film_ids]

    if films:
        database.films.insert_many(films)

    return JSONResponse({"status": "success"})


@router.post("/parse-images")
def parse_images(user: Optional[dict] = Depends(get_current_user), film_id: int = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    images = get_images_by_ids([film_id])[film_id]
    return JSONResponse({"status": "success", "images": images})


@router.post("/download-image")
def download_image(user: Optional[dict] = Depends(get_current_user), film_id: int = Body(..., embed=True), image: dict = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    if image["width"] < image["height"] * 1.3:
        return JSONResponse({"status": "success", "result": "skip"})

    image_name = f'{image["id"]}.webp'
    film_path = os.path.join(os.path.dirname(__file__), "..", "..", "web", "images", "film_images", str(film_id))
    os.makedirs(film_path, exist_ok=True)
    image_path = os.path.join(film_path, image_name)

    if not os.path.isfile(image_path):
        try:
            wget.download(image["url"], image_path)
            result = resize_preview(image_path, 1000, 0)
            assert result["success"]
        except (FileNotFoundError, HTTPError, URLError, ValueError):
            return JSONResponse({"status": "success", "result": "error"})

    return JSONResponse({"status": "success", "result": "add", "url": f"/images/film_images/{film_id}/{image_name}"})


@router.post("/update-film")
def update_film(user: Optional[dict] = Depends(get_current_user), params: FilmForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    film = database.films.find_one({"film_id": params.film_id})

    if not film:
        return JSONResponse({"status": "error", "message": "Указанный фильм не найден. Возможно, он был удалён"})

    film_dict = params.to_dict(film)
    database.films.update_one({"film_id": params.film_id}, {"$set": film_dict}, upsert=True)
    return JSONResponse({"status": "success", "edited": film_dict["edited"]})


@router.post("/remove-film")
def remove_film(user: Optional[dict] = Depends(get_current_user), film_id: int = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    film = database.films.find_one({"film_id": film_id})

    if not film:
        return JSONResponse({"status": "error", "message": "Указанный фильм не найден. Возможно, он уже был удалён"})

    database.films.delete_one({"film_id": film_id})
    return JSONResponse({"status": "success"})


@router.post("/update-banner")
def update_banner(user: Optional[dict] = Depends(get_current_user), film_id: int = Body(..., embed=True), banner_url: str = Body(..., embed=True)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    banner_name = f"{film_id}.jpg"
    banner_path = os.path.join("web", "images", "banners", banner_name)

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            wget.download(banner_url, os.path.join(temp_dir, banner_name))
        except (HTTPError, URLError):
            return JSONResponse({"status": "error", "message": "не удалось скачать изображение"})
        except ValueError:
            return JSONResponse({"status": "error", "message": f'ссылка "{banner_url}" не выглядит как ссылка'})

        result = resize_preview(os.path.join(temp_dir, banner_name))
        if not result["success"]:
            return JSONResponse({"status": "error", "message": result["message"]})

        if os.path.exists(banner_path):
            os.remove(banner_path)

        banner_hash = get_hash(os.path.join(temp_dir, banner_name))
        os.replace(os.path.join(temp_dir, banner_name), banner_path)

    banner_url = f"/images/banners/{film_id}.jpg?v={banner_hash}"
    database.films.update_one({"film_id": film_id}, {"$set": {"banner": banner_url}})
    return JSONResponse({"status": "success", "banner_url": banner_url})


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
