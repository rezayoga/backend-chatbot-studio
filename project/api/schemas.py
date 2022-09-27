from unicodedata import name
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True


class Template_Content(BaseModel):
    parent_id: Optional[str] = None
    content: Optional[str] = None
    payload: Optional[str] = None
    option: Optional[str] = None
    template_id: Optional[str] = None

    class Config:
        orm_mode = True


class Template(BaseModel):
    client: Optional[str] = None
    channel: Optional[str] = None
    channel_account_alias: Optional[str] = None
    template_name: Optional[str] = None
    division_id: Optional[str] = None

    class Config:
        orm_mode = True
