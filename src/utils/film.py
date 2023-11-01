import random
import re
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import requests
from Levenshtein import ratio
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
    params = ["limit=250", "type=screenshot", "type=still", *query_params]
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
    params = [f"movieId={film_id}" for film_id in film_ids]
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


def production_to_query(production: str) -> dict:
    if production == constants.RUSSIA_PRODUCTION:
        return {"countries": {"$in": ["Россия", "СССР"]}}

    if production == constants.KOREAN_PRODUCTION:
        return {"countries": {"$in": ["Корея Южная"]}}

    if production == constants.FOREIGN_PRODUCTION:
        return {"countries": {"$nin": ["Россия", "СССР", "Корея Южная"]}}

    raise ValueError(f'Invalid production "{production}"')


def filter_persons(persons: List[dict], profession: str) -> List[dict]:
    filtered = []

    for person in persons:
        if person["enProfession"] == profession:
            filtered.append({key: value for key, value in person.items() if key not in {"enProfession", "profession"}})

    return filtered


def have_span(spans: Set[Tuple[int, int]], start: int, end: int) -> bool:
    for span_start, span_end in spans:
        if span_start <= start <= span_end:
            return True

        if span_start <= end <= span_end:
            return True

        if start <= span_start and span_end <= end:
            return True

    return False


def hide_names(fact_text: str, film: dict) -> dict:
    spans = set()
    fact_lower = fact_text.lower()
    names = [film["name"], film.get("enName", ""), film.get("alternativeName", "")]
    names = sorted([name for name in names if name], key=lambda film_name: -len(film_name))

    for name in names:
        n_words = len(re.findall(r"[-\w]+", name))
        regexp = f"{re.escape(name.lower())}"

        for match in re.finditer(regexp if n_words >= 2 else f'"{regexp}"|«{regexp}»', fact_lower):
            start, end = match.span()

            if n_words < 2:
                start, end = start + 1, end - 1

            if have_span(spans, start, end):
                continue

            spans.add((start, end))

    for match in re.finditer(r'«[^»]+»|"[^"]+"', fact_lower):
        text = match.group()
        best_ratio = max(ratio(text, name) for name in names)
        start, end = match.span()

        if best_ratio >= 0.8 and not have_span(spans, start + 1, end - 1):
            spans.add((start + 1, end - 1))

    spans = [{"start": start, "end": end} for start, end in sorted(spans)]

    for i, span in enumerate(spans[1:]):
        assert spans[i]["end"] < span["start"]

    return {"value": fact_text, "spans": spans}


def preprocess_facts(facts: Optional[List[dict]], film: dict) -> List[dict]:
    if facts is None:
        return []

    processed_facts = []

    for fact in facts:
        if fact["type"].lower() != "fact":
            continue

        fact_text = BeautifulSoup(fact["value"], "html.parser").text
        processed_facts.append({**hide_names(fact_text, film), "spoiler": fact["spoiler"]})

    return processed_facts
