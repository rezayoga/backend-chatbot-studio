from datetime import date
from typing import Optional, List, Dict, Any

from pydantic import constr, BaseModel, Field



class NameObject(BaseModel):
    formatted_name: str = Field(title="formatted_name", description="The formatted name of the object")
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    prefix: Optional[str] = None


class AddressObject(BaseModel):
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    type: Optional[str] = None


class EmailObject(BaseModel):
    email: Optional[str] = None
    type: Optional[str] = None


class OrgObject(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    company: Optional[str] = None


class PhoneObject(BaseModel):
    phone: Optional[str] = None
    type: Optional[str] = None
    wa_id: Optional[str] = None


class UrlObject(BaseModel):
    url: Optional[str] = None
    type: Optional[str] = None


class ContactObject(BaseModel):
    addresses: Optional[AddressObject] = None
    birthday: Optional[date] = None
    emails: Optional[EmailObject] = None
    name: Optional[NameObject] = Field(title="name", description="Name of the contact")
    phones: Optional[PhoneObject] = None
    org: Optional[OrgObject] = None
    urls: Optional[UrlObject] = None

    class Config:
        orm_mode = True


class MediaObject(BaseModel):
    id: str = Field(title="id", description="The id of the media object")
    link: Optional[str] = None
    caption: Optional[str] = None
    filename: Optional[str] = None
    provider: Optional[str] = None

    class Config:
        orm_mode = True


class Template(BaseModel):
    client: constr(min_length=1)
    channel: constr(min_length=1)
    channel_account_alias: constr(min_length=1)
    template_name: constr(min_length=1)
    template_description: constr(min_length=1)
    division_id: constr(min_length=1)

    class Config:
        orm_mode = True


class ContextObject(BaseModel):
    message_id: str = Field(title="message_id", description="The id of the context object")

    class Config:
        orm_mode = True


class ReplyObject(BaseModel):
    title: constr(min_length=1) = Field(title="title", description="The title of the reply object")
    id: constr(min_length=1) = Field(title="id", description="The id of the reply object")

    class Config:
        orm_mode = True


class ButtonObject(BaseModel):
    text: Optional[str] = None
    id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    reply: Optional[ReplyObject] = None

    class Config:
        orm_mode = True


class ProductObject(BaseModel):
    product_retailer_id: Optional[str] = None

    class Config:
        orm_mode = True


class RowObject(BaseModel):
    id: constr(max_length=24)
    title: constr(max_length=200)
    description: constr(max_length=72)

    class Config:
        orm_mode = True


class SectionObject(BaseModel):
    product_items: Optional[List[ProductObject]] = None
    rows: Optional[List[RowObject]] = None
    title: Optional[str] = None


class ActionObject(BaseModel):
    button: Optional[str] = None
    buttons: Optional[List[ButtonObject]] = None
    catalog_id: Optional[str] = None
    product_retailer_id: Optional[str] = None
    sections: Optional[list[SectionObject]] = None

    class Config:
        orm_mode = True


class HeaderObject(BaseModel):
    document: Optional[MediaObject] = None
    image: Optional[MediaObject] = None
    text: Optional[str] = None
    type: str = Field(title="type", description="The type of the header object. Supported values: text, "
                                                "video, image, document")
    video: Optional[MediaObject] = None

    class Config:
        orm_mode = True


class BodyObject(BaseModel):
    text: str = Field(title="text", description="The text of the body object")

    class Config:
        orm_mode = True


class FooterObject(BaseModel):
    text: str = Field(title="text", description="The text of the footer object")

    class Config:
        orm_mode = True


class InteractiveObject(BaseModel):
    action: ActionObject = Field(title="action", description="The action of the interactive object")
    body: Optional[BodyObject] = None
    footer: Optional[FooterObject] = None
    header: Optional[HeaderObject] = None
    type: str = Field(title="type",
                      description="The type of the interactive object. Supported values: 'button', 'list', 'product', "
                                  "'product_list'")

    class Config:
        orm_mode = True


class LocationObject(BaseModel):
    address: Optional[str] = None
    latitude: Optional[str] = Field(title="latitude", description="The latitude of the location")
    longitude: Optional[str] = Field(title="longitude", description="The longitude of the location")
    name: Optional[str] = None

    class Config:
        orm_mode = True


class TextObject(BaseModel):
    body: str = Field(title="body", description="The body of the text object")
    preview_url: Optional[bool] = None

    class Config:
        orm_mode = True


class LanguageObject(BaseModel):
    policy: str = Field(title="policy", description="The language policy of the message")
    code: str = Field(title="code", description="The language code of the message")

    class Config:
        orm_mode = True


class ButtonParameterObject(BaseModel):
    type: str = Field(title="type", description="The type of the button parameter")
    payload: Optional[str] = None
    text: Optional[str] = None


class ComponentsObject(BaseModel):
    type: str = Field(title="type", description="The type of the component")
    sub_type: Optional[str] = None
    parameters: Optional[List[ButtonParameterObject]] = None
    index: Optional[str] = None

    class Config:
        orm_mode = True


class TemplateObject(BaseModel):
    name: str = Field(title="name", description="The name of the template")
    language: LanguageObject = Field(title="language", description="The language of the template")
    components: Optional[List[ComponentsObject]] = None
    namespace: Optional[str] = None

    class Config:
        orm_mode = True


class ReactionObject(BaseModel):
    message_id: str = Field(title="message_id", description="The message_id of the message to be reacted to")
    emoji: str = Field(title="emoji", description="The emoji to be used for the reaction")

    class Config:
        orm_mode = True


class MessageObject(BaseModel):
    audio: Optional[MediaObject] = None
    contacts: Optional[ContactObject] = None
    context: Optional[ContextObject] = None
    document: Optional[MediaObject] = None
    hsm: Optional[str] = None
    image: Optional[MediaObject] = None
    interactive: Optional[InteractiveObject] = None
    location: Optional[LocationObject] = None
    messaging_product: str = Field(title="messaging_product",
                                   description="The messaging product to use for this message")
    preview_url: Optional[bool] = None
    recipient_type: Optional[str] = None
    status: Optional[str] = None
    sticker: Optional[MediaObject] = None
    template: Optional[TemplateObject] = None
    text: Optional[TextObject] = None
    to: Optional[str] = Field(title="to", description="The phone number of the recipient")
    type: Optional[str] = Field(title="type", description="The type of the message. Supported types: text, image, "
                                                          "document, video, audio, location, contact, sticker, "
                                                          "interactive, reaction")
    video: Optional[MediaObject] = None
    reaction: Optional[ReactionObject] = None

    class Config:
        orm_mode = True


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
    payload: MessageObject = Field(title="payload", description="The payload of the template content")
    option: constr(min_length=1) = Field(title="option", description="The option of the template content")
    template_id: constr(min_length=1) = Field(title="template_id", description="The template_id of the template content")

    class Config:
        orm_mode = True
