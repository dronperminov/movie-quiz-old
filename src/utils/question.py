import random
from collections import defaultdict
from typing import List, Optional, Tuple

from src import constants
from src.database import database
from src.dataclasses.settings import Settings


def get_question_weights(settings: Settings, statistics: List[dict]) -> List[float]:
    query = settings.to_films_query()
    question2exist = {question_type: database.films.find_one({**query, **settings.question_to_query(question_type)}) is not None for question_type in settings.questions}
    last_statistics = [record for record in statistics if record["datetime"] >= settings.last_update]

    if not statistics or not last_statistics:
        return [int(question2exist[question_type]) for question_type in settings.questions]

    question2count = defaultdict(int)

    for record in last_statistics:
        question2count[record["question_type"]] += 1

    return [int(question2exist[question_type]) / (question2count[question_type] + 1) for question_type in settings.questions]


def get_question_params(settings: Settings, username: str) -> Tuple[str, dict]:
    statistics = list(database.statistic.find(
        {"username": username, "question_type": {"$in": settings.questions}}
    ).sort("datetime", -1).limit(constants.QUESTION_STATISTICS_LIMIT))

    question_weights = get_question_weights(settings, statistics)
    question_type = random.choices(settings.questions, weights=question_weights, k=1)[0]

    last_film_ids = [record["film_id"] for record in statistics]
    incorrect_film_ids = list({record["film_id"] for record in statistics if not record["correct"] and record["question_type"] == question_type})
    film_ids_query = {"$in": incorrect_film_ids} if incorrect_film_ids and random.random() < constants.REPEAT_PROBABILITY else {"$nin": list(set(last_film_ids))}

    query = settings.to_query(question_type)
    films = list(database.films.find({**query, "film_id": film_ids_query}, {"film_id": 1, "_id": 0}))

    if not films:
        films = list(database.films.find({**query, "film_id": {"$nin": list(set(last_film_ids[:20]))}}, {"film_id": 1, "_id": 0}))

    if not films:
        films = list(database.films.find(query, {"film_id": 1, "_id": 0}))

    film = database.films.find_one({"film_id": random.choice(films)["film_id"]})

    return question_type, film


def get_question_title(question_type: str, film: dict) -> str:
    film_type = constants.MOVIE_TYPE_TO_RUS[film["type"]]

    if question_type == constants.QUESTION_MOVIE_BY_BANNER:
        return f"Назовите {film_type} по баннеру"

    if question_type == constants.QUESTION_MOVIE_BY_SLOGAN:
        return f"Назовите {film_type} по слогану"

    if question_type == constants.QUESTION_MOVIE_BY_DESCRIPTION:
        return f"Назовите {film_type} по описанию"

    if question_type == constants.QUESTION_MOVIE_BY_SHORT_DESCRIPTION:
        return f"Назовите {film_type} по короткому описанию"

    if question_type == constants.QUESTION_MOVIE_BY_FACTS:
        return f"Назовите {film_type} по фактам"

    if question_type == constants.QUESTION_MOVIE_BY_AUDIO:
        return f"Назовите {film_type} по аудио"

    if question_type == constants.QUESTION_MOVIE_BY_ACTORS:
        return f"Назовите {film_type} по актёрам"

    if question_type == constants.QUESTION_MOVIE_BY_CITE:
        return f"Назовите {film_type} по цитате"

    if question_type == constants.QUESTION_MOVIE_BY_IMAGES:
        return f"Назовите {film_type} по кадрам из него"

    if question_type == constants.QUESTION_YEAR_BY_MOVIE:
        return f'Назовите год выхода {constants.MOVIE_TYPE_TO_GENITIVE_RUS[film["type"]]} "{film["name"]}"'

    raise ValueError(f'Invalid question type "{question_type}"')


def get_question_answer(question_type: str, film: dict) -> str:
    if question_type == constants.QUESTION_YEAR_BY_MOVIE:
        return film["year"]

    return film["name"]


def make_question(question_type: str, film: dict, settings: Settings) -> dict:
    question = {
        "film_id": film["film_id"],
        "type": question_type,
        "title": get_question_title(question_type, film),
        "answer": get_question_answer(question_type, film)
    }

    if question_type == constants.QUESTION_MOVIE_BY_FACTS:
        indices = [i for i in range(len(film.get("facts", [])))]
        question["facts_indices"] = indices if settings.facts_mode == constants.SHOW_ALL_FACTS_MODE else [random.choice(indices)]
    elif question_type == constants.QUESTION_MOVIE_BY_CITE:
        question["cite_index"] = random.choice([i for i in range(len(film.get("cites", [])))])
    elif question_type == constants.QUESTION_MOVIE_BY_IMAGES:
        question["image_index"] = random.choice([i for i in range(len(film.get("images", [])))])
    elif question_type == constants.QUESTION_MOVIE_BY_AUDIO:
        question["audio_index"] = random.choice([i for i in range(len(film.get("audios", [])))])

    return question


def get_question_and_film(username: str, settings: Settings) -> Tuple[Optional[dict], Optional[dict]]:
    question = database.questions.find_one({"username": username})

    if not question:
        return None, None

    if not question["type"] in settings.questions:
        return None, None

    film = database.films.find_one({**settings.to_query(question["type"]), "film_id": question["film_id"]})

    if not film:
        return None, None

    if question["type"] == constants.QUESTION_MOVIE_BY_FACTS:
        if max(question["facts_indices"]) >= len(film.get("facts", [])):
            return None, None

        if len(question["facts_indices"]) > 1 and settings.facts_mode == constants.SHOW_ONE_FACT_MODE:
            return None, None

        if len(question["facts_indices"]) == 1 and len(film.get("facts", [])) > 1 and settings.facts_mode == constants.SHOW_ALL_FACTS_MODE:
            return None, None

    if question["type"] == constants.QUESTION_MOVIE_BY_CITE:
        if question["cite_index"] >= len(film.get("cites", [])):
            return None, None

    if question["type"] == constants.QUESTION_MOVIE_BY_IMAGES:
        if question["image_index"] >= len(film.get("images", [])):
            return None, None

    if question["type"] == constants.QUESTION_MOVIE_BY_AUDIO:
        if question["audio_index"] >= len(film.get("audios", [])):
            return None, None

    return question, film
