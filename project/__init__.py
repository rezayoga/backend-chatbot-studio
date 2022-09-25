from fastapi import FastAPI
from project.celery_utils import create_celery   # new


def create_app() -> FastAPI:
    app = FastAPI()

    from project.logging import configure_logging          # new
    configure_logging()
    # do this before loading routes              # new
    app.celery_app = create_celery()

    from project.templates import templates_router                # new
    app.include_router(templates_router)                      # new

    @app.get("/")
    async def root():
        return {"message": "Started"}

    return app
