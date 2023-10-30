import os
from contextlib import asynccontextmanager
from typing import AsyncContextManager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.config import LOGGING_CONFIG

from src.api.api import router as api_router
from src.api.auth import router as auth_router
from src.api.question import router as question_router
from src.api.settings import router as settings_router
from src.api.statistics import router as statistics_router
from src.database import database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    database.connect()
    yield
    database.close()


app = FastAPI(lifespan=lifespan)


def main() -> None:
    app.include_router(api_router)
    app.include_router(auth_router)
    app.include_router(settings_router)
    app.include_router(question_router)
    app.include_router(statistics_router)

    app.add_middleware(GZipMiddleware, minimum_size=500)

    app.mount("/styles", StaticFiles(directory="web/styles"))
    app.mount("/js", StaticFiles(directory="web/js"))
    app.mount("/fonts", StaticFiles(directory="web/fonts"))
    app.mount("/images", StaticFiles(directory="web/images"))

    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

    host = os.getenv("MOVIE_QUIZ_HOST", "0.0.0.0")
    port = int(os.getenv("MOVIE_QUIZ_PORT", "6543"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
