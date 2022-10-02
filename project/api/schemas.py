from datetime import date
from typing import Optional, List, Dict, Any

from pydantic import validator, BaseModel, Field


class ValidatedBaseModel(BaseModel):
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        _ignored = kwargs.pop('exclude_none')
        return super().dict(*args, exclude_none=True, **kwargs)


class GenericFormatErrorException(Exception):
    """ Custom exception for generic format error """

    def __init__(self, value: object, message: str = None):
        self.value = value
        self.message = message
        super().__init__(self.message)


class GenericMissingRequiredAttributeException(Exception):

    def __init__(self, title: str, message: str = None):
        self.title = title
        self.message = message
        super().__init__(self.message)


class NameObject(BaseModel):
    formatted_name: str = Field(title="formatted_name | Required", description="The formatted name of the object")
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
    name: NameObject = Field(title="name | Required", description="Name of the contact")
    phones: Optional[PhoneObject] = None
    org: Optional[OrgObject] = None
    urls: Optional[UrlObject] = None

    class Config:
        orm_mode = True


class MediaObject(BaseModel):
    id: str = Field(title="id | Required", description="The id of the media object")
    link: Optional[str] = None
    caption: Optional[str] = None
    filename: Optional[str] = None
    provider: Optional[str] = None

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


class ContextObject(BaseModel):
    message_id: Optional[str] = None

    class Config:
        orm_mode = True


class ButtonObject(BaseModel):
    text: Optional[str] = None
    title: Optional[str] = None
    id: Optional[str] = None

    class Config:
        orm_mode = True


class ProductObject(BaseModel):
    product_retailer_id: Optional[str] = None

    class Config:
        orm_mode = True


class RowObject(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

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
    type: str = Field(title="type | Required", description="The type of the header object. Supported values: text, "
                                                           "video, image, document")
    video: Optional[MediaObject] = None

    class Config:
        orm_mode = True


class BodyObject(BaseModel):
    text: Optional[str] = None

    class Config:
        orm_mode = True


class FooterObject(BaseModel):
    text: Optional[str] = None

    class Config:
        orm_mode = True


class InteractiveObject(BaseModel):
    action: ActionObject = Field(title="action | Required", description="The action of the interactive object")
    body: Optional[BodyObject] = None
    footer: Optional[FooterObject] = None
    header: Optional[HeaderObject] = None
    type: str = Field(title="type | Required",
                      description="The type of the interactive object. Supported values: 'button', 'list', 'product', "
                                  "''")

    class Config:
        orm_mode = True


class LocationObject(BaseModel):
    address: Optional[str] = None
    latitude: Optional[str] = Field(title="latitude | Required", description="The latitude of the location")
    longitude: Optional[str] = Field(title="longitude | Required", description="The longitude of the location")
    name: Optional[str] = None

    class Config:
        orm_mode = True


class TextObject(BaseModel):
    body: str = Field(title="body | Required", description="The body of the text object")
    preview_url: Optional[bool] = None

    class Config:
        orm_mode = True


class LanguageObject(BaseModel):
    policy: str = Field(title="policy | Required", description="The language policy of the message")
    code: str = Field(title="code | Required", description="The language code of the message")

    class Config:
        orm_mode = True


class ButtonParameterObject(BaseModel):
    type: str = Field(title="type | Required", description="The type of the button parameter")
    payload: Optional[str] = None
    text: Optional[str] = None


class ComponentsObject(BaseModel):
    type: str = Field(title="type | Required", description="The type of the component")
    sub_type: Optional[str] = None
    parameters: Optional[List[ButtonParameterObject]] = None
    index: Optional[str] = None

    class Config:
        orm_mode = True


class TemplateObject(BaseModel):
    name: str = Field(title="name | Required", description="The name of the template")
    language: LanguageObject = Field(title="language | Required", description="The language of the template")
    components: Optional[List[ComponentsObject]] = None
    namespace: Optional[str] = None

    class Config:
        orm_mode = True


class ReactionObject(BaseModel):
    message_id: str = Field(title="message_id | Required", description="The message_id of the message to be reacted to")
    emoji: str = Field(title="emoji | Required", description="The emoji to be used for the reaction")

    class Config:
        orm_mode = True


class MessageObject(ValidatedBaseModel):
    audio: Optional[MediaObject] = None
    contacts: Optional[ContactObject] = None
    context: Optional[ContextObject] = None
    document: Optional[MediaObject] = None
    hsm: Optional[str] = None
    image: Optional[MediaObject] = None
    interactive: Optional[InteractiveObject] = None
    location: Optional[LocationObject] = None
    messaging_product: str = Field(title="messaging_product | Required",
                                   description="The messaging product to use for this message")
    preview_url: Optional[bool] = None
    recipient_type: Optional[str] = None
    status: Optional[str] = None
    sticker: Optional[MediaObject] = None
    template: Optional[TemplateObject] = None
    text: Optional[TextObject] = None
    to: str = Field(title="to | Required", description="The phone number of the recipient")
    type: Optional[str] = "text"
    video: Optional[MediaObject] = None
    reaction: Optional[ReactionObject] = None

    class Config:
        orm_mode = True

    @validator('audio', 'document', 'image', 'sticker', 'video')
    def validate_media(cls, v):
        if not isinstance(v, MediaObject):
            raise GenericFormatErrorException(v, 'Invalid MediaObject type!')
        return v

    @validator('contacts')
    def validate_contacts(cls, v):
        if not isinstance(v, str):
            raise GenericFormatErrorException(v, 'Invalid ContactObject type!')
        return v

    @validator('context')
    def validate_context(cls, v):
        if not isinstance(v, ContextObject):
            raise GenericFormatErrorException(v, 'Invalid ContextObject type!')
        return v

    @validator('interactive')
    def validate_interactive(cls, v):
        if not isinstance(v, InteractiveObject):
            raise GenericFormatErrorException(v, 'Invalid InteractiveObject type!')
        return v

    @validator('location')
    def validate_location(cls, v):
        if not isinstance(v, LocationObject):
            raise GenericFormatErrorException(v, 'Invalid LocationObject type!')
        return v

    @validator('template')
    def validate_template(cls, v):
        if not isinstance(v, TemplateObject):
            raise GenericFormatErrorException(v, 'Invalid TemplateObject type!')
        return v

    @validator('text')
    def validate_text(cls, v):
        if not isinstance(v, TextObject):
            raise GenericFormatErrorException(v, 'Invalid TextObject type!')
        return v


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
    payload: Optional[MessageObject] = None
    option: Optional[str] = None
    template_id: Optional[str] = None

    class Config:
        orm_mode = True
