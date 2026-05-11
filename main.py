"""FarmaTrack — FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import init_db
from routers import pigs, health, farrowings, pens, scan, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FarmaTrack API",
    description="Pig farm management — herd tracking, health records, farrowing & OCR scanning.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pigs.router)
app.include_router(health.router)
app.include_router(farrowings.router)
app.include_router(pens.router)
app.include_router(scan.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Root"])
def root():
    return {"app": "FarmaTrack", "status": "running"}
