from fastapi import FastAPI, Request, Response
from project.celery_utils import create_celery   # new
from fastapi.openapi.utils import get_openapi


def create_app() -> FastAPI:

    app = FastAPI()

    # Salt to your taste
    ALLOWED_ORIGINS = 'https://localhost:5173'    # or 'foo.com', etc.

    # handle CORS preflight requests
    @app.options('/{rest_of_path:path}')
    async def preflight_handler(request: Request, rest_of_path: str) -> Response:
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS, PUT'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # set CORS headers
    @app.middleware('http')
    async def add_CORS_header(request: Request, call_next):
        response = await call_next(request)
        response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS, PUT'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Chatbot Studio API",
            version="1.0.0",
            description="API docs for Jatis Mobile Chatbot Studio",
            routes=app.routes,
            servers=[{"url": "https://chatbotstudio.rezayogaswara.dev/"}]
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
        return {"message": "App started successfully"}

    return app
