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
from .schemas import User as UserSchema
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
    if not verify_password(password, user.hashed_password):
        return False
    return user


@api_router.post("/templates/")
async def create_template(created_template: TemplateSchema):
    template = Template()
    template.client = created_template.client
    template.channel = created_template.channel
    template.channel_account_alias = created_template.channel_account_alias
    template.template_name = created_template.template_name
    template.division_id = created_template.division_id
    session.add(template)
    session.commit()

    return JSONResponse(status_code=200, content={"message": "Template created successfully!"})


@api_router.get("/templates/", response_model=List[TemplateSchema])
async def get_templates():
    templates = session.query(Template).all()
    if templates is None:
        raise HTTPException(status_code=404, detail="Empty templates")
    return JSONResponse(status_code=200, content=jsonable_encoder(templates))


@api_router.post("/users")
async def create_user(created_user: UserSchema):
    logger.info("create_user() called")
    user = User()
    user.username = created_user.username
    user.email = created_user.email
    user.name = created_user.name
    user.hashed_password = get_password_hash(created_user.password)
    user.is_active = True
    session.add(user)
    session.commit()
    return JSONResponse(status_code=200, content={"message": "User created successfully!"})


@api_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    return {"access_token": user.username, "token_type": "bearer"}
