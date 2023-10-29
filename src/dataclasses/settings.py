from dataclasses import dataclass
from typing import List

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

    @classmethod
    def from_dict(cls: "Settings", data: dict) -> "Settings":
        theme = data.get("theme", "light")
        question_years = data.get("question_years", get_default_question_years())
        questions = data.get("questions", constants.QUESTIONS)
        movie_productions = data.get("movie_productions", constants.PRODUCTIONS)
        movie_types = data.get("movie_types", constants.MOVIE_TYPES)
        top_lists = data.get("top_lists", [])
        stay_actors_open = data.get("stay_actors_open", False)
        return cls(theme, question_years, questions, movie_productions, movie_types, top_lists, stay_actors_open)

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "question_years": self.question_years,
            "questions": self.questions,
            "movie_productions": self.movie_productions,
            "movie_types": self.movie_types,
            "top_lists": self.top_lists,
            "stay_actors_open": self.stay_actors_open
        }

    def to_films_query(self) -> dict:
        query = {
            "$and": [
                {"$or": [{"year": {"$gte": start_year, "$lte": end_year}} for start_year, end_year in self.question_years]},
                {"production": {"$in": self.movie_productions}},
                {"movie_type": {"$in": self.movie_types}}
            ]
        }

        if self.top_lists:
            query["$and"].append({"tops": {"$in": self.top_lists}})

        return query

    def to_query(self, question_type: str = "") -> dict:
        question_types = [question_type] if question_type else self.questions

        query = self.to_films_query()
        query["$and"].append({"$or": [self.__question_to_query(question_type) for question_type in question_types]})
        return query

    def __question_to_query(self, question_type: str) -> dict:
        if question_type == constants.QUESTION_MOVIE_BY_BANNER:
            return {"banner": {"$exists": True, "$regex": ".jpg$"}}

        if question_type == constants.QUESTION_MOVIE_BY_SLOGAN:
            return {"slogan": {"$exists": True, "$ne": None}}

        if question_type == constants.QUESTION_MOVIE_BY_DESCRIPTION:
            return {"description": {"$exists": True, "$ne": None}}

        if question_type == constants.QUESTION_MOVIE_BY_SHORT_DESCRIPTION:
            return {"shortDescription": {"$exists": True, "$ne": None}}

        if question_type == constants.QUESTION_MOVIE_BY_FACTS:
            return {"facts": {"$exists": True, "$nin": [[], None]}}

        if question_type == constants.QUESTION_MOVIE_BY_AUDIO:
            return {"audios": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_MOVIE_BY_ACTORS:
            return {"actors": {"$exists": True, "$ne": []}}

        if question_type == constants.QUESTION_YEARS:
            return {
                "$or": [
                    self.__question_to_query(constants.QUESTION_MOVIE_BY_BANNER),
                    self.__question_to_query(constants.QUESTION_MOVIE_BY_SLOGAN),
                    self.__question_to_query(constants.QUESTION_MOVIE_BY_DESCRIPTION)
                ]
            }

        return {}
