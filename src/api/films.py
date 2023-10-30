from typing import Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import make_error, templates
from src.database import database
from src.dataclasses.film_form import FilmForm
from src.dataclasses.films_query import FilmsQuery
from src.utils.auth import get_current_user
from src.utils.common import get_word_form

router = APIRouter()


@router.get("/films")
def get_films(user: Optional[dict] = Depends(get_current_user), search_params: FilmsQuery = Depends()) -> Response:
    if not user:
        return RedirectResponse(url="/login")

    if search_params.is_empty():
        return RedirectResponse(url="/films")

    settings = database.settings.find_one({"username": user["username"]})
    query = search_params.to_query()
    films = list(database.films.find(query)) if query else []

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
        version=constants.VERSION,
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
        return RedirectResponse(url="/login")

    if user["role"] != "admin":
        return make_error(message="Эта страница доступна только администраторам.", user=user)

    film = database.films.find_one({"film_id": film_id})

    if not film:
        return make_error(message="Запрашиваемого фильма не существует", user=user)

    settings = database.settings.find_one({"username": user["username"]})
    template = templates.get_template("films/film.html")
    content = template.render(
        user=user,
        settings=settings,
        page="film",
        version=constants.VERSION,
        film=film,
        movie_types=constants.MOVIE_TYPES,
        movie_type2rus=constants.MOVIE_TYPE_TO_RUS,
        top_lists=constants.TOP_LISTS,
        top_list2rus=constants.TOP_LIST_TO_RUS
    )
    return HTMLResponse(content=content)


@router.post("/update-film")
def update_film(user: Optional[dict] = Depends(get_current_user), params: FilmForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    if user["role"] != "admin":
        return JSONResponse({"status": "error", "message": "Пользователь не является администратором"})

    film = database.films.find_one({"film_id": params.film_id})

    if not film:
        return JSONResponse({"status": "error", "message": "Указанный фильм не найден. Возможно, он был удалён"})

    database.films.update_one({"film_id": params.film_id}, {"$set": params.to_dict()}, upsert=True)
    return JSONResponse({"status": "success"})


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
