from unicodedata import name
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CreateUser(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None

class Template_Content(BaseModel):
    id: Optional[str] = None
    parent_id: Optional[str] = None
    content: Optional[str] = None
    payload: Optional[str] = None
    option: Optional[str] = None
    created_at: Optional[datetime] = None
    template_id: Optional[str] = None

    class Config:
        orm_mode = True


class Template(BaseModel):
    id: Optional[str] = None
    client: Optional[str] = None
    channel: Optional[str] = None
    channel_account_alias: Optional[str] = None
    created_at: Optional[datetime] = None
    template_name: Optional[str] = None
    division_id: Optional[str] = None
    template_contents: Optional[List[Template_Content]] = None

    class Config:
        orm_mode = True
