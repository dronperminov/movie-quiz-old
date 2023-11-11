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
    correct2count = dict()
    incorrect2count = dict()
    percents = dict()

    statistic_documents = list(database.statistic.find({**query}, {"correct": 1, "question_type": 1, "_id": 0}))

    for question_type in constants.QUESTIONS:
        question_docs = [doc for doc in statistic_documents if doc["question_type"] == question_type]
        correct = sum(doc["correct"] for doc in question_docs)
        incorrect = len(question_docs) - correct

        correct2count[question_type] = correct
        incorrect2count[question_type] = incorrect
        percents[question_type] = correct / max(correct + incorrect, 1)

    correct_score = sum(correct2count[question_type] * constants.QUESTION_TO_WEIGHT[question_type] for question_type in constants.QUESTIONS)
    incorrect_score = sum(incorrect2count[question_type] * constants.QUESTION_TO_WEIGHT[question_type] for question_type in constants.QUESTIONS)
    score = correct_score / max(correct_score + incorrect_score, 1)

    correct_questions = sum(correct2count.values())
    incorrect_questions = sum(incorrect2count.values())
    total_questions = correct_questions + incorrect_questions

    return {
        "show_questions_count": settings.show_questions_count,
        "questions_form": get_word_form(total_questions, ["вопросов", "вопроса", "вопрос"]),
        "score": {
            "value": round(score * 100, 1),
            "correct": correct_score,
            "incorrect": incorrect_score
        },
        "questions": {
            "correct": correct_questions,
            "incorrect": incorrect_questions,
            "total": total_questions
        },
        "correct2count": correct2count,
        "incorrect2count": incorrect2count,
        "percents": percents
    }
