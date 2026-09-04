"""
FastAPI main application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from core.redis import redis_client
from routes import research, health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("veritymesh")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle management."""
    logger.info("Starting VerityMesh API...")
    await redis_client.connect()
    logger.info("Redis connected.")
    yield
    await redis_client.disconnect()
    logger.info("VerityMesh API shut down.")


app = FastAPI(
    title="VerityMesh API",
    description="Autonomous multi-agent research & fact-verification platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(research.router)


@app.get("/")
async def root():
    return {
        "name": "VerityMesh API",
        "version": "0.1.0",
        "docs": "/docs",
    }
