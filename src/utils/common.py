from datetime import datetime
from typing import List

from src import constants


def get_default_question_years() -> List[List[int]]:
    years = []

    for i, year in enumerate(constants.QUESTION_YEARS[1:]):
        years.append([constants.QUESTION_YEARS[i], year - 1])

    years.append([constants.QUESTION_YEARS[-1], datetime.now().year])
    return years


def get_word_form(questions: int, word_forms: List[str]) -> str:
    if questions % 10 in {0, 5, 6, 7, 8, 9} or questions in {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}:
        return word_forms[0]

    if questions % 10 in {2, 3, 4}:
        return word_forms[1]

    return word_forms[2]
