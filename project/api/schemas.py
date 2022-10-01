from operator import index
from unicodedata import name
import pydantic
from typing import Optional, List
from datetime import datetime


class ContactObject(pydantic.BaseModel):
    addresses: Optional[str] = None
    birthday: Optional[str] = None
    emails: Optional[str] = None
    name: Optional[str] = None
    phones: Optional[str] = None
    org: Optional[str] = None
    urls: Optional[str] = None

    class Config:
        orm_mode = True


class MediaObject(pydantic.BaseModel):
    id: Optional[str] = None
    link: Optional[str] = None
    caption: Optional[str] = None
    filename: Optional[str] = None
    provider: Optional[str] = None

    class Config:
        orm_mode = True


class Template(pydantic.BaseModel):
    client: Optional[str] = None
    channel: Optional[str] = None
    channel_account_alias: Optional[str] = None
    template_name: Optional[str] = None
    division_id: Optional[str] = None

    class Config:
        orm_mode = True


class ContextObject(pydantic.BaseModel):
    message_id: Optional[str] = None

    class Config:
        orm_mode = True


class ButtonObject(pydantic.BaseModel):
    text: Optional[str] = None
    title: Optional[str] = None
    id: Optional[str] = None

    class Config:
        orm_mode = True


class ProductObject(pydantic.BaseModel):
    product_retailer_id: Optional[str] = None

    class Config:
        orm_mode = True


class RowObject(pydantic.BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


class SectionObject(pydantic.BaseModel):
    product_items: Optional[List[ProductObject]] = None
    rows: Optional[List[RowObject]] = None
    title: Optional[str] = None


class ActionObject(pydantic.BaseModel):
    button: Optional[str] = None
    buttons: Optional[List[ButtonObject]] = None
    catalog_id: Optional[str] = None
    product_retailer_id: Optional[str] = None
    sections: Optional[list[SectionObject]] = None

    class Config:
        orm_mode = True


class HeaderObject(pydantic.BaseModel):

    document: Optional[MediaObject] = None
    image: Optional[MediaObject] = None
    text: Optional[str] = None
    type: Optional[str] = None
    video: Optional[MediaObject] = None

    class Config:
        orm_mode = True


class BodyObject(pydantic.BaseModel):
    text: Optional[str] = None

    class Config:
        orm_mode = True


class FooterObject(pydantic.BaseModel):
    text: Optional[str] = None

    class Config:
        orm_mode = True


class InteractiveObject(pydantic.BaseModel):
    action: Optional[ActionObject] = None
    body: Optional[BodyObject] = None
    footer: Optional[FooterObject] = None
    header: Optional[HeaderObject] = None
    type: Optional[str] = None

    class Config:
        orm_mode = True


class LocationObject(pydantic.BaseModel):
    address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    name: Optional[str] = None

    class Config:
        orm_mode = True


class TextObject(pydantic.BaseModel):
    body: Optional[str] = None
    preview_url: Optional[bool] = None

    class Config:
        orm_mode = True


class LanguageObject(pydantic.BaseModel):
    policy: Optional[str] = None
    code: Optional[str] = None

    class Config:
        orm_mode = True


class ButtonParameterObject(pydantic.BaseModel):
    type: Optional[str] = None
    payload: Optional[str] = None
    text: Optional[str] = None


class ComponentsObject(pydantic.BaseModel):
    type: Optional[str] = None
    sub_type: Optional[str] = None
    parameters: Optional[List[ButtonParameterObject]] = None
    index: Optional[str] = None

    class Config:
        orm_mode = True


class TemplateObject(pydantic.BaseModel):
    name: Optional[str] = None
    language: Optional[LanguageObject] = None
    components: Optional[List[ComponentsObject]] = None
    namespace: Optional[str] = None

    class Config:
        orm_mode = True


class MessageObject(pydantic.BaseModel):
    audio: Optional[MediaObject] = None
    contacts: Optional[ContactObject] = None
    context: Optional[ContextObject] = None
    document: Optional[MediaObject] = None
    hsm: Optional[str] = None
    image: Optional[MediaObject] = None
    interactive: Optional[InteractiveObject] = None
    location: Optional[LocationObject] = None
    messaging_product: Optional[str] = None
    preview_url: Optional[bool] = None
    recipient_type: Optional[str] = None
    status: Optional[str] = None
    sticker: Optional[MediaObject] = None
    template: Optional[TemplateObject] = None
    text: Optional[TextObject] = None
    to: Optional[str] = None
    type: Optional[str] = None
    video: Optional[MediaObject] = None

    class Config:
        orm_mode = True


class User(pydantic.BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True


class Template_Content(pydantic.BaseModel):
    parent_id: Optional[str] = None
    payload: Optional[MessageObject] = None
    option: Optional[str] = None
    template_id: Optional[str] = None

    class Config:
        orm_mode = True
