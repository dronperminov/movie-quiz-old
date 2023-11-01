from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.database import database
from src.dataclasses.statistic_form import StatisticForm
from src.utils.auth import get_current_user

router = APIRouter()


@router.post("/add-statistic")
def add_statistic(user: Optional[dict] = Depends(get_current_user), params: StatisticForm = Depends()) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    database.statistic.insert_one({"datetime": datetime.now(), "username": user["username"], **params.to_dict()})
    database.questions.delete_one({"username": user["username"]})
    return JSONResponse({"status": "success"})


@router.post("/clear-statistic")
def clear_statistic(user: Optional[dict] = Depends(get_current_user)) -> JSONResponse:
    if not user:
        return JSONResponse({"status": "error", "message": "Пользователь не залогинен"})

    database.statistic.delete_many({"username": user["username"]})
    return JSONResponse({"status": "success"})
