import random
import re
from collections import defaultdict
from typing import Dict, List, Optional, Set

import requests
from bs4 import BeautifulSoup

from src import constants
from src.api import tokens


def api_request(url: str) -> Optional[dict]:
    token = random.choice(tokens)

    response = requests.get(f"https://api.kinopoisk.dev{url}", headers={
        "accept": "application/json",
        "X-API-KEY": token
    })

    if response.status_code == 200:
        return response.json()

    # TODO: handle 403 error (day limit)
    return None


def get_films(query_params: List[str]) -> dict:
    params = ["limit=250", *query_params]
    fields = [
        "id", "name", "type", "enName", "year",
        "slogan", "description", "shortDescription",
        "rating", "movieLength", "backdrop", "genres",
        "countries", "persons", "top250", "facts",
        "videos", "poster", "alternativeName"
    ]

    for field in fields:
        params.append(f"selectFields={field}")

    return api_request(f'/v1.3/movie?{"&".join(params)}')


def get_images(query_params: List[str]) -> dict:
    params = ["limit=250", "type=screenshot", *query_params]
    return api_request(f'/v1/image?{"&".join(params)}')


def get_films_by_ids(film_ids: List[int]) -> List[dict]:
    if not film_ids:
        return []

    params = [f"id={film_id}" for film_id in film_ids]
    response = get_films(params)
    films = response["docs"]

    while response["page"] < response["pages"]:
        print(f'films {response["page"] + 1} / {response["pages"]}')  # noqa
        response = get_films(params + [f'page={response["page"] + 1}'])
        films.extend(response["docs"])

    return films


def get_top_films() -> List[dict]:
    top_params = [f"top250={i + 1}" for i in range(250)]
    response = get_films(top_params)
    films = response["docs"]

    while response["page"] < response["pages"]:
        print("films", response["page"] + 1, "/", response["pages"])  # noqa
        response = get_films(top_params + [f'page={response["page"] + 1}'])
        films.extend(response["docs"])

    return films


def get_images_by_ids(film_ids: List[int]) -> Dict[int, List[dict]]:
    params = [f"id={film_id}" for film_id in film_ids]
    response = get_images(params)
    images = response["docs"]

    while response["page"] < response["pages"]:
        print(response["page"], "/", response["pages"])  # noqa
        response = get_images(params + [f'page={response["page"] + 1}'])
        images.extend(response["docs"])

    film_id2images = defaultdict(list)

    for image in images:
        film_id2images[image["movieId"]].append(image)

    return film_id2images


def get_film_production(countries: Set[str]) -> List[str]:
    productions = []

    if countries.intersection({"СССР", "Россия"}):
        productions.append(constants.RUSSIA_PRODUCTION)

    if countries.difference({"СССР", "Россия"}):
        productions.append(constants.FOREIGN_PRODUCTION)

    return productions


def filter_persons(persons: List[dict], profession: str) -> List[dict]:
    filtered = []

    for person in persons:
        if person["enProfession"] == profession:
            filtered.append({key: value for key, value in person.items() if key not in {"enProfession", "profession"}})

    return filtered


def hide_names(fact_text: str, film: dict) -> dict:
    spans = []
    fact_lower = fact_text.lower()

    for name in [film["name"], film.get("enName", ""), film.get("alternativeName", "")]:
        if not name:
            continue

        n_words = len(re.findall(r"[-\w]+", name))
        regexp = f"{re.escape(name.lower())}"

        for match in re.finditer(regexp if n_words >= 2 else f'"{regexp}"|«{regexp}»', fact_lower):
            start, end = match.span()

            if n_words < 2:
                start, end = start + 1, end - 1

            print(f'{film["name"]}: {match.group()} ({fact_text[start:end]})')
            spans.append({"start": start, "end": end})

    return {"value": fact_text, "spans": spans}


def preprocess_facts(facts: Optional[List[dict]], film: dict) -> List[dict]:
    if facts is None:
        return []

    processed_facts = []

    for fact in facts:
        fact_text = BeautifulSoup(fact["value"], "html.parser").text
        processed_facts.append({**hide_names(fact_text, film), "type": fact["type"], "spoiler": fact["spoiler"]})

    return processed_facts
