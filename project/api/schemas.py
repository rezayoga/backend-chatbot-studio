from datetime import date, timedelta
from typing import Optional, List, Union

from pydantic import constr, BaseModel, Field, EmailStr


class NameObject(BaseModel):
	formatted_name: str = Field(title="formatted_name", description="The formatted name of the object")
	first_name: Optional[str] = None
	middle_name: Optional[str] = None
	last_name: Optional[str] = None
	suffix: Optional[str] = None
	prefix: Optional[str] = None

	class Config:
		orm_mode = True


class AddressObject(BaseModel):
	street: Optional[str] = None
	city: Optional[str] = None
	state: Optional[str] = None
	zip: Optional[str] = None
	country: Optional[str] = None
	country_code: Optional[str] = None
	type: Optional[str] = None

	class Config:
		orm_mode = True


class EmailObject(BaseModel):
	email: Optional[str] = None
	type: Optional[str] = None

	class Config:
		orm_mode = True


class OrgObject(BaseModel):
	title: Optional[str] = None
	department: Optional[str] = None
	company: Optional[str] = None

	class Config:
		orm_mode = True


class PhoneObject(BaseModel):
	phone: Optional[str] = None
	type: Optional[str] = None
	wa_id: Optional[str] = None

	class Config:
		orm_mode = True


class UrlObject(BaseModel):
	url: Optional[str] = None
	type: Optional[str] = None

	class Config:
		orm_mode = True


class ContactObject(BaseModel):
	addresses: Optional[AddressObject] = None
	birthday: Optional[date] = None
	emails: Optional[List[EmailObject]] = None
	name: Optional[NameObject] = Field(title="name", description="Name of the contact")
	phones: Optional[List[PhoneObject]] = None
	org: Optional[OrgObject] = None
	urls: Optional[List[UrlObject]] = None

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
	id: constr(max_length=128)
	title: constr(max_length=256)
	description: constr(max_length=256)

	class Config:
		orm_mode = True


class SectionObject(BaseModel):
	product_items: Optional[List[ProductObject]] = None
	rows: Optional[List[RowObject]] = None
	title: Optional[str] = None

	class Config:
		orm_mode = True


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

	class Config:
		orm_mode = True


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


class MessageObjectPayload(BaseModel):
	audio: Optional[MediaObject] = Field(title="audio", description="The audio of the message")
	contacts: Optional[List[ContactObject]] = None
	context: Optional[ContextObject] = None
	document: Optional[MediaObject] = None
	hsm: Optional[str] = None
	image: Optional[MediaObject] = None
	interactive: Optional[InteractiveObject] = None
	location: Optional[LocationObject] = None
	messaging_product: Optional[str] = Field(title="messaging_product",
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


""" Application Schemas """


class Option_Position(BaseModel):
	x: int = Field(title="x", description="The x position of the option")
	y: int = Field(title="y", description="The y position of the option")

	class config:
		orm_mode = True


class Parent_Id(BaseModel):
	parent_id: str = Field(title="parent_id", description="The parent_id of the message")
	option: str = Field(title="option", description="The option of the message")
	option_label: str = Field(title="option_label", description="The option_label of the message")
	option_position: Option_Position = Field(title="option_position",
	                                         description="The option_position of the message")

	class Config:
		orm_mode = True


class User_Login(BaseModel):
	username: str = Field(title="username", description="The username of the user")
	password: str = Field(title="password", description="The password of the user")

	class Config:
		orm_mode = True


class User(BaseModel):
	username: constr(min_length=1)
	email: EmailStr = None
	password: constr(min_length=1) = Field(title="password", description="The password of the user")
	name: constr(min_length=1)
	is_active: Optional[bool] = True

	class Config:
		orm_mode = True


class Template(BaseModel):
	client_id: Optional[str] = None
	channel_id: Optional[str] = None
	account_id: Optional[str] = None
	account_alias: Optional[str] = None
	template_name: constr(min_length=1) = None
	template_description: Optional[str] = None
	division_id: Optional[str] = None
	is_deleted: Optional[bool] = False

	class Config:
		orm_mode = True


class Template_Update(BaseModel):
	client_id: Optional[str] = None
	channel_id: Optional[str] = None
	account_id: Optional[str] = None
	account_alias: Optional[str] = None
	template_name: constr(min_length=1)
	template_description: Optional[str] = None
	division_id: Optional[str] = None

	class Config:
		orm_mode = True


class Template_Content(BaseModel):
	parent_ids: Optional[Union[List[Parent_Id], None]] = Field(title="parent_ids",
	                                                           description="The list of template_content's parent_id")
	payloads: List[MessageObjectPayload] = Field(title="payloads",
	                                             description="The payloads of the template content")
	template_id: constr(min_length=1) = Field(title="template_id",
	                                          description="The template_id of the template content")
	label: Optional[str] = None
	position: Optional[Option_Position] = None
	is_deleted: Optional[bool] = False

	class Config:
		orm_mode = True


class Template_Content_Update(BaseModel):
	parent_ids: Optional[Union[List[Parent_Id], None]] = Field(title="parent_ids",
	                                                           description="The list of template_content's parent_id")
	payloads: Optional[List[MessageObjectPayload]] = Field(title="payloads",
	                                                       description="The payloads of the template content")
	template_id: Optional[str] = Field(title="template_id",
	                                   description="The template_id of the template content")
	label: Optional[str] = None
	position: Optional[Option_Position] = None
	is_deleted: Optional[bool] = False

	class Config:
		orm_mode = True


# set denylist enabled to True
# you can set to check access or refresh token or even both of them
class JWT_Settings(BaseModel):
	authjwt_secret_key: str = "d4d2b169f9c91008caf5cb68c9e4125a16bf139469de01f98fe8ac03ed8f8d0a"
	authjwt_denylist_enabled: bool = True
	authjwt_denylist_token_checks: set = {"access", "refresh"}
	access_token_expires: int = timedelta(minutes=15)
	refresh_token_expires: int = timedelta(days=30)
