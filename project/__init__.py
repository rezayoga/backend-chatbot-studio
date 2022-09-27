from fastapi import FastAPI
from project.celery_utils import create_celery   # new
from fastapi.openapi.utils import get_openapi


def create_app() -> FastAPI:
    app = FastAPI()

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Chatbot Studio API",
            version="1.0.0",
            description="API schema for Jatis Mobile Chatbot Studio",
            routes=app.routes,
            servers=[{"url": "https://chatbotstudio.rezayogaswara.dev"}]
        )
        """ openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        } """
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    from project.logging import configure_logging          # new
    configure_logging()
    # do this before loading routes              # new
    app.celery_app = create_celery()

    from project.api import api_router                # new
    app.include_router(api_router)                      # new

    @app.get("/")
    async def root():
        return {"message": "Started"}

    return app
