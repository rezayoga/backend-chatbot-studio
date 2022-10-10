import logging
from typing import List

from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from passlib.handlers.bcrypt import bcrypt
from redis import Redis
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from project.api.models import *
# from project.database import SessionLocal
from project.api.services import *
from . import api_router
from .schemas import JWT_Settings as JWT_SettingsSchema
from .schemas import Template as TemplateSchema
from .schemas import Template_Update as Template_UpdateSchema
from .schemas import Template_Content as Template_ContentSchema
from .schemas import User as UserSchema
from .schemas import User_Login as User_LoginSchema
from ..database import async_session

logger = logging.getLogger(__name__)
# session = SessionLocal()
settings = JWT_SettingsSchema()

""" Exception Handler """


# Dependency
async def get_session() -> AsyncSession:
	async with async_session() as session:
		yield session


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


def get_user_exception():
	credentials_exception = HTTPException(
		status_code=401,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	return credentials_exception


""" auth """


# def get_password_hash(password: str):
# 	return bcrypt.hash(password)
#
#
# def verify_password(plain_password, hashed_password):
# 	return bcrypt.verify(plain_password, hashed_password)
#
#
# def authenticate_user(username: str, password: str):
# 	user = session.query(User) \
# 		.filter(User.username == username) \
# 		.first()
# 	if not user:
# 		return False
# 	if not verify_password(password, user.hashed_password):
# 		return False
# 	return user


@AuthJWT.load_config
def get_config():
	return settings


redis_connection = Redis(host='localhost', port=6379, db=0, decode_responses=True)


# A storage engine to save revoked tokens. in production,
# you can use Redis for storage system
# denylist = set()


# For this example, we are just checking if the tokens jti
# (unique identifier) is in the denylist set. This could
# be made more complex, for example storing the token in Redis
# with the value true if revoked and false if not revoked
@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
	jti = decrypted_token['jti']
	entry = redis_connection.get(jti)
	return entry and entry == 'true'


@api_router.post("/token/", tags=["auth"])
async def login(user: User_LoginSchema, auth: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
	# Check if username and password match
	user = authenticate_user(user.username, user.password, session)
	if not user:
		raise incorrect_request_exception("Incorrect username or password")

	access_token = auth.create_access_token(subject=user.id)
	refresh_token = auth.create_refresh_token(subject=user.id)
	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"token_type": "bearer",
		"expires_in": settings.access_token_expires
	}


@api_router.post("/token/refresh/", tags=["auth"])
async def refresh_access_token(auth: AuthJWT = Depends()):
	auth.jwt_refresh_token_required()
	current_user = auth.get_jwt_subject()
	new_access_token = auth.create_access_token(subject=current_user)
	return {"access_token": new_access_token}


@api_router.delete("/access/revoke/", tags=["auth"])
async def access_revoke(auth: AuthJWT = Depends()):
	auth.jwt_required()
	jti = auth.get_raw_jwt()['jti']
	# denylist.add(jti)
	redis_connection.setex(jti, settings.access_token_expires, 'true')
	return {"message": "Access token revoked"}


@api_router.delete("/refresh/revoke/", tags=["auth"])
async def refresh_revoke(auth: AuthJWT = Depends()):
	auth.jwt_refresh_token_required()
	jti = auth.get_raw_jwt()['jti']
	# denylist.add(jti)
	redis_connection.setex(jti, settings.refresh_token_expires, 'true')
	return {"message": "Refresh token revoked"}

#
# @api_router.post("/users/", tags=["auth"])
# async def create_user(created_user: UserSchema):
# 	user = User()
# 	user.username = created_user.username
# 	user.email = created_user.email
# 	user.name = created_user.name
# 	user.hashed_password = get_password_hash(created_user.password)
# 	user.is_active = True
# 	session.add(user)
# 	session.commit()
# 	return JSONResponse(status_code=200, content={"message": "User created successfully"})
#
#
# """ templates """
#
#
# @api_router.post("/templates/", tags=["templates"])
# async def create_template(created_template: TemplateSchema, auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template = Template()
# 	template.client = created_template.client
# 	template.channel = created_template.channel
# 	template.channel_account_alias = created_template.channel_account_alias
# 	template.template_name = created_template.template_name
# 	template.template_description = created_template.template_description
# 	template.division_id = created_template.division_id
# 	template.owner_id = auth.get_jwt_subject()
# 	session.add(template)
# 	session.commit()
#
# 	logging.log(logging.INFO, template)
#
# 	data = jsonable_encoder(template)
#
# 	logging.log(logging.INFO, data)
# 	return JSONResponse(status_code=200, content={"message": "Template created successfully", "body": data})
#
#
# @api_router.get("/templates/{template_id}/", tags=["templates"])
# async def get_template_by_template_id(template_id: str, auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template = session.query(Template) \
# 		.filter(Template.id == template_id) \
# 		.filter(Template.owner_id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if template is None:
# 		raise not_found_exception("Template not found")
#
# 	return JSONResponse(status_code=200, content=jsonable_encoder(template))
#
#
# @api_router.get("/templates/", tags=["templates"], response_model=List[TemplateSchema])
# async def get_templates():
# 	templates = session.query(Template).all()
# 	if templates is None or len(templates) == 0:
# 		raise not_found_exception("Templates not found")
# 	return JSONResponse(status_code=200, content=jsonable_encoder(templates))
#
#
# @api_router.get("/user/templates/", tags=["templates"])
# async def get_templates_by_user_id(auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	templates = session.query(Template) \
# 		.filter(Template.owner_id == auth.get_jwt_subject()) \
# 		.all()
#
# 	if templates is None or len(templates) == 0:
# 		raise not_found_exception("Templates not found")
#
# 	return JSONResponse(status_code=200, content=jsonable_encoder(templates))
#
#
# @api_router.put("/templates/{template_id}/", tags=["templates"])
# async def update_template(template_id: str, updated_template: Template_UpdateSchema, auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template = session.query(Template) \
# 		.filter(Template.id == template_id) \
# 		.filter(Template.owner_id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if template is None:
# 		raise not_found_exception("Template not found")
#
# 	template.client = updated_template.client
# 	template.channel_account_alias = updated_template.channel_account_alias
# 	template.template_name = updated_template.template_name
# 	template.template_description = updated_template.template_description
# 	template.division_id = updated_template.division_id
# 	session.commit()
# 	logging.log(logging.INFO, template)
# 	data = jsonable_encoder(updated_template.from_orm(template).dict(exclude_none=True))
# 	logging.log(logging.INFO, data)
# 	return JSONResponse(status_code=200, content={"message": "Template updated successfully", "body": data})
#
#
# @api_router.delete("/templates/{template_id}/", tags=["templates"])
# async def delete_template(template_id: str, auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template = session.query(Template) \
# 		.filter(Template.id == template_id) \
# 		.filter(Template.owner_id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if template is None:
# 		raise not_found_exception("Template not found")
#
# 	session.delete(template)
# 	session.commit()
#
# 	return JSONResponse(status_code=200, content={"message": "Template deleted successfully"})
#
#
# """ template contents """
#
#
# @api_router.post("/template-contents/", tags=["template-contents"])
# async def create_template_content(created_template_content: Template_ContentSchema,
#                                   auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template = session.query(Template) \
# 		.filter(Template.id == created_template_content.template_id) \
# 		.first()
#
# 	if template is None:
# 		raise not_found_exception("Template not found")
#
# 	payload = jsonable_encoder(created_template_content.payload.dict(exclude_none=True))
# 	template_content = Template_Content()
# 	template_content.template_id = created_template_content.template_id
# 	template_content.parent_id = created_template_content.parent_id
# 	template_content.payload = payload
# 	template_content.option = created_template_content.option
# 	template_content.x = created_template_content.x
# 	template_content.y = created_template_content.y
# 	template_content.option_label = created_template_content.option_label
# 	template_content.option_position = created_template_content.option_position
# 	session.add(template_content)
# 	session.commit()
#
# 	logging.log(logging.INFO, template_content)
#
# 	data = jsonable_encoder(template_content)
#
# 	logging.log(logging.INFO, data)
#
# 	return JSONResponse(status_code=200, content={"message": "Template content created successfully", "body": data})
#
#
# @api_router.get("/template-contents/{template_id}/", tags=["template-contents"])
# async def get_template_contents_by_template_id(template_id: str, auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template = session.query(Template) \
# 		.filter(Template.id == template_id) \
# 		.filter(Template.owner_id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if template is None:
# 		raise not_found_exception("Template not found")
#
# 	template_contents = session.query(Template_Content) \
# 		.filter(Template_Content.template_id == template_id) \
# 		.all()
#
# 	if template_contents is None or len(template_contents) == 0:
# 		raise not_found_exception("Template contents not found")
#
# 	return template_contents
#
#
# @api_router.get("/template/template-contents/{template_content_id}/", tags=["template-contents"])
# async def get_template_content_by_template_content_id(template_content_id: str,
#                                                       auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template_content = session.query(Template_Content) \
# 		.filter(Template_Content.id == template_content_id) \
# 		.first()
#
# 	if template_content is None:
# 		raise not_found_exception("Template content not found")
#
# 	template = session.query(Template) \
# 		.filter(Template.id == template_content.template_id) \
# 		.filter(and_(Template.owner_id == auth.get_jwt_subject())) \
# 		.first()
#
# 	if template is None:
# 		raise not_found_exception("Template not found")
#
# 	return template_content
#
#
# @api_router.put("/template-contents/{template_content_id}/", tags=["template-contents"])
# async def update_template_content(template_content_id: str, updated_template_content: Template_ContentSchema,
#                                   auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template = session.query(Template) \
# 		.filter(Template.id == updated_template_content.template_id) \
# 		.filter(Template.owner_id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if template is None:
# 		raise not_found_exception("Template not found")
#
# 	template_content = session.query(Template_Content) \
# 		.filter(Template_Content.id == template_content_id) \
# 		.first()
#
# 	if template_content is None:
# 		raise not_found_exception("Template content not found")
#
# 	payload = jsonable_encoder(updated_template_content.payload)
# 	template_content.template_id = updated_template_content.template_id
# 	template_content.parent_id = updated_template_content.parent_id
# 	template_content.payload = payload
# 	template_content.option = updated_template_content.option
# 	template_content.x = updated_template_content.x
# 	template_content.y = updated_template_content.y
# 	template_content.option_label = updated_template_content.option_label
# 	template_content.option_position = updated_template_content.option_position
# 	session.commit()
# 	logging.log(logging.INFO, template_content)
# 	data = jsonable_encoder(updated_template_content.from_orm(template_content).dict(exclude_none=True))
# 	logging.log(logging.INFO, data)
# 	return JSONResponse(status_code=200, content={"message": "Template content updated successfully", "body": data})
#
#
# @api_router.delete("/template-contents/{template_content_id}/", tags=["template-contents"])
# async def delete_template_content(template_content_id: str, auth: AuthJWT = Depends()):
# 	auth.jwt_required()
# 	user = session.query(User) \
# 		.filter(User.id == auth.get_jwt_subject()) \
# 		.first()
#
# 	if user is None:
# 		raise get_user_exception()
#
# 	template_content = session.query(Template_Content) \
# 		.filter(Template_Content.id == template_content_id) \
# 		.first()
#
# 	if template_content is None:
# 		raise not_found_exception("Template content not found")
#
# 	session.delete(template_content)
# 	session.commit()
# 	return JSONResponse(status_code=200, content={"message": "Template content deleted successfully"})
#
#
# """ users """
#
#
# @api_router.get("/users/", tags=["users"], response_model=List[UserSchema])
# async def get_users():
# 	users = session.query(User).all()
# 	if users is None:
# 		raise not_found_exception("Empty users")
# 	return JSONResponse(status_code=200, content=jsonable_encoder(users))
