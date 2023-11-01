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
    description: str = Body(..., embed=True)
    short_description: str = Body(..., embed=True)
    countries: List[str] = Body(..., embed=True)
    genres: List[str] = Body(..., embed=True)
    length: Optional[int] = Body(..., embed=True)
    tops: List[str] = Body(..., embed=True)
    facts: List[dict] = Body(..., embed=True)

    def to_dict(self) -> dict:
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
            "facts": self.facts
        }
