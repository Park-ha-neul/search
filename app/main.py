from fastapi import Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
import os

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users, search, images, documents, videos, audios, hdfs

from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .config import settings

templates = Jinja2Templates(directory="templates")

load_dotenv()  # take environment variables from .env.

# app = FastAPI(dependencies=[Depends(get_query_token)])
app = FastAPI(
    title="T3Q.search API", description="T3Q.search 를 위한 API 입니다", version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(images.router)
app.include_router(documents.router)
app.include_router(videos.router)
app.include_router(audios.router)
app.include_router(hdfs.router)
"""
app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)
"""


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


# Usage
# $ pipenv run uvicorn app.main:app --reload
