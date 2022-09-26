import logging
import uuid
from typing import List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from project.database import SessionLocal
from project.templates.models import *

from . import templates_router
from .schemas import Template as TemplateSchema
from .schemas import CreateUsers as CreateUserSchema
from passlib.context import CryptContext

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)
session = SessionLocal()


def get_password_hash(password: str):
    return bcrypt.hash(password)


@templates_router.get("/create/")
async def create():
    logger.info("create() called")

    session.add(Template(id=uuid.uuid4(), template_name=uuid.uuid4()))
    session.commit()

    return JSONResponse(status_code=200, content={"message": "success"})


@templates_router.get("/read/", response_model=List[TemplateSchema])
async def read():
    logger.info("read() called")

    templates = session.query(Template).all()
    if templates is None:
        raise HTTPException(status_code=404, detail="Empty templates")
    return JSONResponse(status_code=200, content=jsonable_encoder(templates))


@templates_router.post("/create/user")
async def create_user(created_user: CreateUserSchema) -> User:
    logger.info("create_user() called")
    user = User()
    user.username = created_user.username
    user.email = created_user.email
    user.name = created_user.name
    user.hashed_password = get_password_hash(created_user.password)
    user.is_active = True
    session.add(user)
    session.commit()

    return user
