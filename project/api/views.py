import logging
import uuid
from typing import List, Optional
import os
from webbrowser import get
from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from project.database import SessionLocal
from project.api.models import *

from . import api_router
from .schemas import Template as TemplateSchema
from .schemas import User as UserSchema
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from project import api
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e75945f34a"
ALGORITHM = "HS256"

oauth_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

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


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        if username is None or id is None:
            raise get_user_exception()
        return {"username": username, "id": id}
    except JWTError:
        raise get_user_exception()
    

#Exception
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response


@api_router.get("/templates/user", tags=["templates"])
async def read_all_templates_by_user(user: dict = Depends(get_current_user)):

    if user is None:
        raise get_user_exception()

    return session.query(Template)\
        .filter(Template.owner_id == user.id)\
        .all()


@api_router.post("/templates/", tags=["templates"])
async def create_template(created_template: TemplateSchema):
    template = Template()
    template.client = created_template.client
    template.channel = created_template.channel
    template.channel_account_alias = created_template.channel_account_alias
    template.template_name = created_template.template_name
    template.division_id = created_template.division_id
    template.owner_id = created_template.owner_id
    session.add(template)
    session.commit()

    return JSONResponse(status_code=200, content={"message": "Template created successfully"})


@api_router.get("/templates/", tags=["templates"], response_model=List[TemplateSchema])
async def get_templates():
    templates = session.query(Template).all()
    if templates is None:
        raise HTTPException(status_code=404, detail="Empty templates")
    return JSONResponse(status_code=200, content=jsonable_encoder(templates))


@api_router.get("/users/", tags=["users"], response_model=List[UserSchema])
async def get_users():
    users = session.query(User).all()
    if users is None:
        raise HTTPException(status_code=404, detail="Empty users")
    return JSONResponse(status_code=200, content=jsonable_encoder(users))


@api_router.post("/users/", tags=["users"])
async def create_user(created_user: UserSchema):
    user = User() 
    user.username = created_user.username
    user.email = created_user.email
    user.name = created_user.name
    user.hashed_password = get_password_hash(created_user.password)
    user.is_active = True
    session.add(user)
    session.commit()
    return JSONResponse(status_code=200, content={"message": "User created successfully"})


@api_router.post("/token/", tags=["users"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    token_expires = timedelta(minutes=15)
    token = create_access_token(user.username, user.id, token_expires)
    return {"access_token": token, "token_type": "bearer"}
