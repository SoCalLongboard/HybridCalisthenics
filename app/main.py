from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.catalog import load_catalog
from app.db import init_db
from app.routers import admin, auth, catalog, progress, sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_catalog()  # fail fast on startup if catalog.json is malformed
    yield


app = FastAPI(title="Hybrid Routine Tracker", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(catalog.router)
app.include_router(progress.router)
app.include_router(sessions.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
