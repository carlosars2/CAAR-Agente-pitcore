"""FastAPI application — Pitcore Agent API gateway."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, health, whatsapp
from src.config.settings import settings
from src.memory.redis_memory import memory

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pitcore Agent API",
    description="Agente de IA da Pitcore & Systems — atendimento inteligente para centros automotivos.",
    version="1.0.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(whatsapp.router, prefix="/api")


@app.on_event("startup")
async def startup():
    logger.info("Pitcore Agent starting — env=%s, model=%s", settings.app_env, settings.anthropic_model)


@app.on_event("shutdown")
async def shutdown():
    await memory.close()
    logger.info("Pitcore Agent shutdown complete")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env != "production",
    )
