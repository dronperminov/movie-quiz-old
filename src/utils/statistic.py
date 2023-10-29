import datetime
from typing import Optional

from src.database import database
from src.utils.common import get_word_form


def get_statistic(username: str, day_start: Optional[datetime.datetime] = None, day_end: Optional[datetime.datetime] = None) -> dict:
    query = {"username": username}

    if day_start is not None and day_end is not None:
        query["datetime"] = {"$gte": day_start, "$lte": day_end}

    # общие вопросы
    correct_questions = database.statistic.count_documents({**query, "correct": True})
    incorrect_questions = database.statistic.count_documents({**query, "correct": False})
    total_questions = correct_questions + incorrect_questions

    return {
        "questions_form": get_word_form(correct_questions, ["вопросов", "вопроса", "вопрос"]),
        "questions": {
            "correct": correct_questions,
            "incorrect": incorrect_questions,
            "total": total_questions
        }
    }
