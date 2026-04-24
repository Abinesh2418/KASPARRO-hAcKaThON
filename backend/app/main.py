from fastapi import FastAPI
from app.core.middleware import setup_cors, setup_exception_handlers
from app.api.router import router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Curio API",
        description="AI-powered fashion shopping assistant — Groq chat + Gemma4 visual search",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    setup_cors(app)
    setup_exception_handlers(app)
    app.include_router(router)
    return app


app = create_app()
