from dataclasses import dataclass
from typing import List, Optional

from fastapi import Body


@dataclass
class FilmForm:
    film_id: int = Body(..., embed=True)
    name: str = Body(..., embed=True)
    movie_type: str = Body(..., embed=True)
    year: int = Body(..., embed=True)
    slogan: str = Body(..., embed=True)
    description: dict = Body(..., embed=True)
    short_description: dict = Body(..., embed=True)
    countries: List[str] = Body(..., embed=True)
    genres: List[str] = Body(..., embed=True)
    length: Optional[int] = Body(..., embed=True)
    tops: List[str] = Body(..., embed=True)
    facts: List[dict] = Body(..., embed=True)
    cites: List[dict] = Body(..., embed=True)

    def to_dict(self, film: dict) -> dict:
        return {
            "name": self.name,
            "type": self.movie_type,
            "year": self.year,
            "slogan": self.slogan,
            "description": self.description,
            "shortDescription": self.short_description,
            "countries": self.countries,
            "genres": self.genres,
            "length": self.length,
            "tops": self.tops,
            "facts": self.facts,
            "cites": self.cites,
            "edited": self.__is_edited(film)
        }

    def __is_edited(self, film: dict) -> bool:
        if film.get("edited", False):
            return True

        if film["name"] != self.name:
            return True

        if film["type"] != self.movie_type:
            return True

        if film.get("year", -1) != self.year:
            return True

        if film.get("slogan", "") != self.slogan:
            return True

        if film["description"]["value"] != self.description["value"] or film["description"]["spans"] != self.description["spans"]:
            return True

        if film["shortDescription"]["value"] != self.short_description["value"] or film["shortDescription"]["spans"] != self.short_description["spans"]:
            return True

        if set(film.get("countries", [])) != set(self.countries):
            return True

        if set(film.get("genres", [])) != set(self.genres):
            return True

        if film.get("length", -1) != self.length:
            return True

        if set(film.get("tops", [])) != set(self.tops):
            return True

        if len(film.get("facts", [])) != len(self.facts):
            return True

        for film_fact, fact in zip(film["facts"], self.facts):
            if film_fact["value"] != fact["value"] or film_fact["spans"] != fact["spans"]:
                return True

        if len(film.get("cites", [])) != len(self.cites):
            return True

        for film_cite, cite in zip(film["cites"], self.cites):
            if film_cite["value"] != cite["value"] or film_cite["spans"] != cite["spans"]:
                return True

        return False
