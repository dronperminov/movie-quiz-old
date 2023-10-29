from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src import constants
from src.api import templates
from src.database import database
from src.dataclasses.settings import Settings
from src.dataclasses.user import User
from src.utils import auth

router = APIRouter()


@router.get("/login")
def login_get(user: Optional[dict] = Depends(auth.get_current_user)) -> Response:
    if user:
        return RedirectResponse(url="/", status_code=302)

    template = templates.get_template("login.html")
    return HTMLResponse(content=template.render(page="login", version=constants.VERSION))


@router.post("/sign-in")
def sign_in(username: str = Body(..., embed=True), password: str = Body(..., embed=True)) -> JSONResponse:
    user = database.users.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}})

    if user is None:
        return JSONResponse({"status": "error", "message": f'Пользователя "{username}" не существует'})

    if not auth.validate_password(password, user["password_hash"]):
        return JSONResponse({"status": "error", "message": "Имя пользователя или пароль введены неверно"})

    access_token = auth.create_access_token(user["username"])
    response = JSONResponse(content={"status": "success", "token": access_token})
    response.set_cookie(key=auth.COOKIE_NAME, value=access_token, httponly=True)
    return response


@router.post("/sign-up")
def sign_up(username: str = Body(..., embed=True), password: str = Body(..., embed=True), fullname: str = Body(..., embed=True)) -> JSONResponse:
    user = database.users.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}})

    if user is not None:
        return JSONResponse({"status": "error", "message": f'Пользователь "{username}" уже существует'})

    settings = Settings.from_dict({})
    user = User(username=username, password_hash=auth.get_password_hash(password), fullname=fullname, settings=settings)

    database.users.insert_one(asdict(user))
    access_token = auth.create_access_token(username)
    response = JSONResponse(content={"status": "success", "token": access_token})
    response.set_cookie(key=auth.COOKIE_NAME, value=access_token, httponly=True)
    return response


@router.get("/logout")
def logout() -> Response:
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(auth.COOKIE_NAME)
    return response
