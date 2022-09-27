import logging
import uuid
from typing import List

from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from project.database import SessionLocal
from project.api.models import *

from . import api_router
from .schemas import Template as TemplateSchema
from .schemas import CreateUser as CreateUserSchema
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm

from project import api

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)
session = SessionLocal()


def get_password_hash(password: str):
    return bcrypt.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = session.query(User)\
        .filter(User.username == username)\
        .first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@api_router.get("/create/")
async def create():
    logger.info("create() called")

    session.add(Template(id=uuid.uuid4(), template_name=uuid.uuid4()))
    session.commit()

    return JSONResponse(status_code=200, content={"message": "success"})


@api_router.get("/read/", response_model=List[TemplateSchema])
async def read():
    logger.info("read() called")

    templates = session.query(Template).all()
    if templates is None:
        raise HTTPException(status_code=404, detail="Empty templates")
    return JSONResponse(status_code=200, content=jsonable_encoder(templates))


@api_router.post("/create/user")
async def create_user(created_user: CreateUserSchema):
    logger.info("create_user() called")
    user = User()
    user.username = created_user.username
    user.email = created_user.email
    user.name = created_user.name
    user.hashed_password = get_password_hash(created_user.password)
    user.is_active = True
    session.add(user)
    session.commit()

    return JSONResponse(status_code=200, content=jsonable_encoder(user))

@api_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.hashed_password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    return {"access_token": user.username, "token_type": "bearer"}
