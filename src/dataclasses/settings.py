from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from src import constants
from src.utils.common import get_default_question_years


@dataclass
class Settings:
    theme: str
    question_years: List[List[int]]
    questions: List[str]
    movie_productions: List[str]
    movie_types: List[str]
    top_lists: List[str]
    stay_actors_open: bool
    last_update: datetime

    @classmethod
    def from_dict(cls: "Settings", data: Optional[dict]) -> "Settings":
        if data is None:
            data = {}

        theme = data.get("theme", "light")
        question_years = data.get("question_years", get_default_question_years())
        questions = data.get("questions", constants.QUESTIONS)
        movie_productions = data.get("movie_productions", constants.PRODUCTIONS)
        movie_types = data.get("movie_types", constants.MOVIE_TYPES)
        top_lists = data.get("top_lists", [])
        stay_actors_open = data.get("stay_actors_open", False)
        last_update = data.get("last_update", datetime(1900, 1, 1))
        return cls(theme, question_years, questions, movie_productions, movie_types, top_lists, stay_actors_open, last_update)

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "question_years": self.question_years,
            "questions": self.questions,
            "movie_productions": self.movie_productions,
            "movie_types": self.movie_types,
            "top_lists": self.top_lists,
            "stay_actors_open": self.stay_actors_open,
            "last_update": self.last_update
        }

    def to_films_query(self) -> dict:
        query = {
            "$and": [
                {"$or": [{"year": {"$gte": start_year, "$lte": end_year}} for start_year, end_year in self.question_years]},
                {"production": {"$in": self.movie_productions}},
                {"type": {"$in": self.movie_types}}
            ]
        }

        if self.top_lists:
            query["$and"].append({"tops": {"$in": self.top_lists}})

        return query

    def to_query(self, question_type: str = "") -> dict:
        question_types = [question_type] if question_type else self.questions

        query = self.to_films_query()
        query["$and"].append({"$or": [self.question_to_query(question_type) for question_type in question_types]})
        return query

    def question_to_query(self, question_type: str) -> dict:
        if question_type == constants.QUESTION_MOVIE_BY_BANNER:
            return {"backdrop.previewUrl": {"$exists": True, "$ne": None}}

        if question_type == constants.QUESTION_MOVIE_BY_SLOGAN:
            return {"slogan": {"$exists": True, "$ne": ""}}

        if question_type == constants.QUESTION_MOVIE_BY_DESCRIPTION:
            return {"description.value": {"$ne": ""}}

        if question_type == constants.QUESTION_MOVIE_BY_SHORT_DESCRIPTION:
            return {"shortDescription.value": {"$ne": ""}}

        if question_type == constants.QUESTION_MOVIE_BY_FACTS:
            return {"facts": {"$exists": True, "$nin": [[], None]}}

        if question_type == constants.QUESTION_MOVIE_BY_AUDIO:
            return {"audios": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_MOVIE_BY_ACTORS:
            return {"actors": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_MOVIE_BY_IMAGES:
            return {"images": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_YEAR_BY_MOVIE:
            return {
                "$or": [
                    self.question_to_query(constants.QUESTION_MOVIE_BY_BANNER),
                    self.question_to_query(constants.QUESTION_MOVIE_BY_SLOGAN),
                    self.question_to_query(constants.QUESTION_MOVIE_BY_DESCRIPTION)
                ]
            }

        raise ValueError(f'Unhandled question_type "{question_type}"')
