import json
import os
import re
from typing import List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError

import wget
from Levenshtein import ratio
from bs4 import BeautifulSoup

from src import constants


def production_to_query(production: str) -> dict:
    if production == constants.RUSSIA_PRODUCTION:
        return {"countries": {"$in": ["Россия", "СССР"]}}

    if production == constants.KOREAN_PRODUCTION:
        return {"countries": {"$in": ["Корея Южная"]}}

    if production == constants.TURKISH_PRODUCTION:
        return {"countries": {"$in": ["Турция"]}}

    if production == constants.FOREIGN_PRODUCTION:
        return {"countries": {"$nin": ["Россия", "СССР", "Корея Южная", "Турция"]}}

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


def get_available_names(movie_name: str) -> List[str]:
    movie_name = re.sub(r" \([^)]+\)", "", movie_name)
    names = {movie_name, movie_name.replace("ё", "е"), movie_name.replace("е", "э")}

    for part in re.split(r"\s+/\s+", movie_name):
        names.add(part)

    new_names = []
    for name in names:
        new_name = name
        for from_digit, to_digit in [("1", "I"), ("2", "II"), ("3", "III"), ("4", "IV"), ("5", "V")]:
            new_name = new_name.replace(from_digit, to_digit)
        new_names.append(new_name)
    names.update(new_names)

    return list(names)


def is_valid_film_name(film: dict, film_data: dict) -> bool:
    if film["year"] != film_data["year"]:
        return False

    for name in get_available_names(film_data["name"]):
        for film_name in film["names"]:
            if re.match(rf"^{re.escape(name.lower())}$", film_name, re.I):
                return True

    return False


def add_cites(films: List[dict]) -> None:
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "data", "cites", "movies.json"), "r", encoding="utf-8") as f:
        movies = json.load(f)

    with open(os.path.join(os.path.dirname(__file__), "..", "..", "data", "cites", "cites.json"), "r", encoding="utf-8") as f:
        movie2cites = json.load(f)

    for movie in movies:
        test_films = [film for film in films if is_valid_film_name(film, movie)]

        if len(test_films) == 1 and not test_films[0]["cites"]:
            test_films[0]["cites"] = [hide_names(cite, test_films[0]) for cite in movie2cites[movie["url"]]]


def download_banner(film: dict, loops: int = 3) -> None:
    backdrop = film.pop("backdrop")
    if backdrop is None or backdrop["previewUrl"] is None:
        return

    banner_path = os.path.join(os.path.dirname(__file__), "..", "..", "web", "images", "banners", f'{film["film_id"]}.jpg')

    for _ in range(loops):
        try:
            wget.download(backdrop["previewUrl"], banner_path)
            film["banner"] = f'/images/banners/{film["film_id"]}.jpg'
            return
        except (FileNotFoundError, HTTPError, URLError, ValueError):
            continue


def preprocess_film(film: dict, images: List[dict]) -> Optional[dict]:
    if film["year"] is None or film["name"] is None:
        return None

    film_id = film["id"]

    names = list({name["name"] for name in film.get("names", [])})
    description = film["description"] if film["description"] is not None else ""
    short_description = film["shortDescription"] if film["shortDescription"] is not None else ""

    countries = [country["name"] for country in film["countries"]]
    genres = [genre["name"] for genre in film["genres"]]
    directors = filter_persons(film["persons"], "director")
    actors = filter_persons(film["persons"], "actor")

    film_data = {
        "film_id": film_id,
        "backdrop": film["backdrop"],
        "name": film["name"],
        "names": names,
        "type": film["type"],
        "poster": film["poster"],
        "year": film["year"],
        "slogan": film["slogan"] if film["slogan"] is not None else "",
        "description": hide_names(description, film),
        "shortDescription": hide_names(short_description, film),
        "countries": countries,
        "genres": genres,
        "actors": actors,
        "directors": directors,
        "length": film["movieLength"],
        "rating": film["rating"],
        "votes": film["votes"],
        "images": [image for image in images if image["width"] >= image["height"] * 1.3],
        "videos": film.get("videos", []),
        "cites": [],
        "facts": preprocess_facts(film["facts"], film),
        "tops": [],
        "topPositions": []
    }

    return film_data
