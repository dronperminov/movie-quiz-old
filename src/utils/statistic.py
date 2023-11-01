import datetime
from typing import Optional

from src import constants
from src.database import database
from src.dataclasses.settings import Settings
from src.utils.common import get_word_form


def get_statistic(username: str, day_start: Optional[datetime.datetime] = None, day_end: Optional[datetime.datetime] = None) -> dict:
    query = {"username": username}
    settings = Settings.from_dict(database.settings.find_one(query))

    if day_start is not None and day_end is not None:
        query["datetime"] = {"$gte": day_start, "$lte": day_end}

    # общие вопросы
    correct_questions2count = dict()
    incorrect_questions2count = dict()
    percents = dict()

    for question_type in constants.QUESTIONS:
        correct = database.statistic.count_documents({**query, "correct": True, "question_type": question_type})
        incorrect = database.statistic.count_documents({**query, "correct": False, "question_type": question_type})
        percent = correct / max(correct + incorrect, 1)

        correct_questions2count[question_type] = correct
        incorrect_questions2count[question_type] = incorrect
        percents[question_type] = percent * constants.QUESTION_TO_WEIGHT[question_type]

    score = sum(percents.values()) / sum(constants.QUESTION_TO_WEIGHT.values())
    correct_questions = sum(correct_questions2count.values())
    incorrect_questions = sum(incorrect_questions2count.values())
    total_questions = correct_questions + incorrect_questions

    return {
        "show_questions_count": settings.show_questions_count,
        "questions_form": get_word_form(total_questions, ["вопросов", "вопроса", "вопрос"]),
        "score": round(score * 100, 1),
        "percents": percents,
        "questions": {
            "correct": correct_questions,
            "incorrect": incorrect_questions,
            "total": total_questions
        },
        "correct2count": correct_questions2count,
        "incorrect2count": incorrect_questions2count
    }
