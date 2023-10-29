from dataclasses import dataclass
from typing import List

from src import constants
from src.utils.common import get_default_question_years


@dataclass
class Settings:
    theme: str
    question_years: List[List[int]]
    questions: List[str]
    movie_production: List[str]
    movie_types: List[str]
    top_lists: List[str]
    stay_actors_open: bool

    @classmethod
    def from_dict(cls: "Settings", data: dict) -> "Settings":
        theme = data.get("theme", "light")
        question_years = data.get("question_years", get_default_question_years())
        questions = data.get("questions", constants.QUESTIONS)
        movie_production = data.get("movie_production", constants.PRODUCTIONS)
        movie_types = data.get("movie_types", constants.MOVIE_TYPES)
        top_lists = data.get("top_lists", [])
        stay_actors_open = data.get("stay_actors_open", False)
        return cls(theme, question_years, questions, movie_production, movie_types, top_lists, stay_actors_open)

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "question_years": self.question_years,
            "questions": self.questions,
            "movie_production": self.movie_production,
            "movie_types": self.movie_types,
            "top_lists": self.top_lists,
            "stay_actors_open": self.stay_actors_open
        }
