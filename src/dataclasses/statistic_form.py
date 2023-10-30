from dataclasses import dataclass

from fastapi import Body


@dataclass
class StatisticForm:
    question_type: str = Body(..., embed=True)
    film_id: int = Body(..., embed=True)
    correct: bool = Body(..., embed=True)

    def to_dict(self) -> dict:
        return {
            "question_type": self.question_type,
            "film_id": self.film_id,
            "correct": self.correct
        }
