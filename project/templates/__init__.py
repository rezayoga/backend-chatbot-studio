from fastapi import APIRouter

templates_router = APIRouter(
    prefix="/templates/v1",
)

from . import views, models, tasks, schemas  # noqa
