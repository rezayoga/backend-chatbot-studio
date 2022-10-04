import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from project.api.models import *
from project.database import SessionLocal
from . import api_router
from .schemas import Template as TemplateSchema
from .schemas import Template_Content as Template_ContentSchema
from .schemas import User as UserSchema

SECRET_KEY: str = "d4d2b169f9c91008caf5cb68c9e4125a16bf139469de01f98fe8ac03ed8f8d0a"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

oauth_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)
session = SessionLocal()


def get_password_hash(password: str):
    return bcrypt.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = session.query(User) \
        .filter(User.username == username) \
        .first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(username: str, id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# Exception
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


def not_found_exception(message: str):
    not_found_exception_response = HTTPException(
        status_code=404,
        detail=message,
    )
    return not_found_exception_response


def incorrect_request_exception(message: str):
    incorrect_request_exception_response = HTTPException(
        status_code=400,
        detail=message,
    )
    return incorrect_request_exception_response


async def get_current_user(token: str = Depends(oauth_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id_: int = payload.get("id")
        if username is None or id_ is None:
            raise get_user_exception()
        return {"username": username, "id": id_}
    except JWTError:
        raise get_user_exception()


""" auth """


@api_router.post("/token/", tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.username, user.id, access_token_expires)

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(user.username, user.id, refresh_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES}


@api_router.post("/token/refresh/", tags=["auth"])
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id_: int = payload.get("id")
        if username is None or id_ is None:
            raise token_exception()
        user = session.query(User) \
            .filter(User.username == username) \
            .first()
        if not user:
            raise token_exception()
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.username, user.id, access_token_expires)
        return {"access_token": access_token, "token_type": "bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES}
    except JWTError:
        raise token_exception()


@api_router.post("/users/", tags=["auth"])
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


""" templates """


@api_router.post("/templates/", tags=["templates"])
async def create_template(created_template: TemplateSchema, user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    template = Template()
    template.client = created_template.client
    template.channel = created_template.channel
    template.channel_account_alias = created_template.channel_account_alias
    template.template_name = created_template.template_name
    template.template_description = created_template.template_description
    template.division_id = created_template.division_id
    template.owner_id = user.get('id')
    session.add(template)
    session.commit()

    data = jsonable_encoder(template.to_dict())

    return JSONResponse(status_code=200, content={"message": "Template created successfully", "data": data})


@api_router.get("/templates/{template_id}/", tags=["templates"])
async def get_template_by_template_id(template_id: str, user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    template = session.query(Template) \
        .filter(Template.id == template_id) \
        .filter(Template.owner_id == user.get('id')) \
        .first()

    if template is None:
        raise not_found_exception("Template not found")

    return template


@api_router.get("/templates/", tags=["templates"], response_model=List[TemplateSchema])
async def get_templates():
    templates = session.query(Template).all()
    if templates is None:
        raise not_found_exception("Templates not found")
    return JSONResponse(status_code=200, content=jsonable_encoder(templates))


@api_router.get("/templates/user/", tags=["templates"])
async def get_templates_by_user_id(user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    return session.query(Template) \
        .filter(Template.owner_id == user.get('id')) \
        .all()


@api_router.put("/templates/{template_id}/", tags=["templates"])
async def update_template(template_id: str, updated_template: TemplateSchema, user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    template = session.query(Template) \
        .filter(Template.id == template_id) \
        .filter(Template.owner_id == user.get('id')) \
        .first()

    if template is None:
        raise not_found_exception("Template not found")

    template.client = updated_template.client
    template.channel = updated_template.channel
    template.channel_account_alias = updated_template.channel_account_alias
    template.template_name = updated_template.template_name
    template.template_description = updated_template.template_description
    template.division_id = updated_template.division_id
    session.commit()

    return JSONResponse(status_code=200, content={"message": "Template updated successfully"})


@api_router.delete("/templates/{template_id}/", tags=["templates"])
async def delete_template(template_id: str, user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    template = session.query(Template) \
        .filter(Template.id == template_id) \
        .filter(Template.owner_id == user.get('id')) \
        .first()

    if template is None:
        raise not_found_exception("Template not found")

    session.delete(template)
    session.commit()

    return JSONResponse(status_code=200, content={"message": "Template deleted successfully"})


""" template contents """


@api_router.post("/template-contents/", tags=["template-contents"])
async def create_template_content(created_template_content: Template_ContentSchema,
                                  user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    template = session.query(Template) \
        .filter(Template.id == created_template_content.template_id) \
        .first()

    if template is None:
        raise not_found_exception("Template not found")

    payload = jsonable_encoder(created_template_content.payload.dict(exclude_none=True))
    template_content = Template_Content()
    template_content.template_id = created_template_content.template_id
    template_content.parent_id = created_template_content.parent_id
    template_content.payload = payload
    template_content.option = created_template_content.option
    session.add(template_content)
    session.commit()
    return JSONResponse(status_code=200, content={"message": "Template content created successfully"})


@api_router.get("/template-contents/{template_id}/", tags=["template-contents"])
async def get_template_contents_by_template_id(template_id: str, user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    template = session.query(Template) \
        .filter(Template.id == template_id) \
        .filter(Template.owner_id == user.get('id')) \
        .first()

    if template is None:
        raise not_found_exception("Template not found")

    template_contents = session.query(Template_Content) \
        .filter(Template_Content.template_id == template_id) \
        .all()

    if template_contents is None:
        raise not_found_exception("Template contents not found")

    return template_contents


@api_router.put("/template-contents/{template_content_id}/", tags=["template-contents"])
async def update_template_content(template_content_id: str, updated_template_content: Template_ContentSchema,
                                  user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    template = session.query(Template) \
        .filter(Template.id == updated_template_content.template_id) \
        .filter(Template.owner_id == user.get('id')) \
        .first()

    if template is None:
        raise not_found_exception("Template not found")

    template_content = session.query(Template_Content) \
        .filter(Template_Content.id == template_content_id) \
        .first()

    if template_content is None:
        raise not_found_exception("Template content not found")

    payload = jsonable_encoder(updated_template_content.payload)
    template_content.template_id = updated_template_content.template_id
    template_content.parent_id = updated_template_content.parent_id
    template_content.payload = payload
    template_content.option = updated_template_content.option
    session.commit()
    return JSONResponse(status_code=200, content={"message": "Template content updated successfully"})


@api_router.delete("/template-contents/{template_content_id}/", tags=["template-contents"])
async def delete_template_content(template_content_id: str, user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    template_content = session.query(Template_Content) \
        .filter(Template_Content.id == template_content_id) \
        .first()

    if template_content is None:
        raise not_found_exception("Template content not found")

    session.delete(template_content)
    session.commit()
    return JSONResponse(status_code=200, content={"message": "Template content deleted successfully"})


""" users """


@api_router.get("/users/", tags=["users"], response_model=List[UserSchema])
async def get_users():
    users = session.query(User).all()
    if users is None:
        raise not_found_exception("Empty users")
    return JSONResponse(status_code=200, content=jsonable_encoder(users))
