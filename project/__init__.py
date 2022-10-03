from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from project.celery_utils import create_celery  # new


def create_app() -> FastAPI:
    app = FastAPI(title="Chatbot Studio API",
                  version="1.0.0",
                  description="API docs for Jatis Mobile Chatbot Studio",
                  contact={
                      "name": "Reza Yogaswara",
                      "url": "https://me.rezayogaswara.dev/",
                      "email": "reza.yoga@gmail.com",
                  },
                  servers=[{"url": "https://chatbotstudio.rezayogaswara.dev/api/v1/", "description": "Development -> "
                                                                                                     "Staging"}])

    # Salt to your taste
    ALLOWED_ORIGINS = 'https://localhost:5173'  # or 'foo.com', etc.

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

    from project.logging import configure_logging  # new
    configure_logging()
    # do this before loading routes              # new
    app.celery_app = create_celery()

    from fastapi.exceptions import RequestValidationError
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    from project.api import api_router  # new
    app.include_router(api_router)  # new

    @app.get("/")
    async def root():
        return {"message": "App started successfully"}

    return app
