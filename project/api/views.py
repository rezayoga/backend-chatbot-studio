import logging

from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from redis import Redis
from sqlalchemy.exc import IntegrityError

# from project.database import SessionLocal
from project.api.dal import *
from . import api_router
from .schemas import JWT_Settings as JWT_SettingsSchema
from .schemas import Template as TemplateSchema, Template_Update as Template_UpdateSchema, \
	Template_Content as Template_ContentSchema, \
	Template_Content_Update as Template_Content_UpdateSchema
from .schemas import User as UserSchema
from .schemas import User_Login as User_LoginSchema
from ..database import get_session

logger = logging.getLogger(__name__)
# session = SessionLocal()
settings = JWT_SettingsSchema()

""" Exception Handler """


# Dependency


def not_found_exception(message: str):
	not_found_exception_response = HTTPException(
		status_code=200,
		detail=jsonable_encoder({"message": message, "data": {}}),
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


@AuthJWT.load_config
def get_config():
	return settings


redis_connection = Redis(host='rezayogaswara.com', username='reza', password='reza1985', port=6379, db=5, decode_responses=True)


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


@api_router.post("/token/", tags=["auth"])
async def login(user: User_LoginSchema, auth: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
	# Check if username and password match
	user = await User_DAL.auth_user(user.username, user.password, session)
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


""" users """


@api_router.get("/users/", tags=["users"])
async def get_users(session: AsyncSession = Depends(get_session)):
	users = await User_DAL.get_users(session)
	return users


@api_router.post("/users/", tags=["auth"])
async def create_user(created_user: UserSchema, session: AsyncSession = Depends(get_session)):
	user = User_DAL.create_user(created_user, session)
	try:
		await session.commit()
		return user
	except IntegrityError as ex:
		await session.rollback()
		raise incorrect_request_exception("Username already exists")


""" templates """


@api_router.post("/templates/", tags=["templates"])
async def create_template(created_template: TemplateSchema, auth: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = Template_DAL.create_template(user.id, created_template, session)
	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template created successfully",
		                                              "body": jsonable_encoder(template)})
	except IntegrityError as ex:
		await session.rollback()
		raise incorrect_request_exception("Incorrect request")


@api_router.get("/templates/{template_id}/", tags=["templates"])
async def get_template_by_template_id(template_id: str, auth: AuthJWT = Depends(),
                                      session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = await Template_DAL.get_template_by_template_id(auth.get_jwt_subject(), template_id, session)

	if template is None or template == False:
		raise not_found_exception("Template not found")

	return template


@api_router.get("/templates/", tags=["templates"], response_model=List[TemplateSchema])
async def get_templates(session: AsyncSession = Depends(get_session)):
	templates = await Template_DAL.get_templates(session)

	# if templates is None or templates == False:
	# 	raise not_found_exception("Templates not found")

	return templates


@api_router.get("/user/templates/", tags=["templates"])
async def get_templates_by_user_id(auth: AuthJWT = Depends(),
                                   session: AsyncSession = Depends(get_session)):
	auth.jwt_required()

	templates = await Template_DAL.get_template_by_user_id(auth.get_jwt_subject(), session)

	if templates is None or templates == False:
		raise not_found_exception("Templates not found")

	return templates


@api_router.put("/templates/{template_id}/", tags=["templates"])
async def update_template(template_id: str, updated_template: Template_UpdateSchema, auth: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = await Template_DAL.update_template(user.id, template_id, updated_template, session)

	if template is None or template == False:
		raise not_found_exception("Template not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template updated successfully",
		                                              "body": jsonable_encoder(template)})
	except IntegrityError as ex:
		await session.rollback()
		raise incorrect_request_exception("Incorrect request")


@api_router.delete("/templates/{template_id}/", tags=["templates"])
async def delete_template(template_id: str, auth: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = await Template_DAL.delete_template(user.id, template_id, session)

	if template is None or template == False:
		raise not_found_exception("Template not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template deleted successfully",
		                                              "body": jsonable_encoder(template)})
	except IntegrityError as ex:
		await session.rollback()
		raise incorrect_request_exception("Incorrect request")


""" template contents """


@api_router.get("/template-contents/", tags=["template-contents"], response_model=List[Template_ContentSchema],
                response_model_exclude_none=True)
async def get_template_contents(session: AsyncSession = Depends(get_session)):
	template_contents = await Template_Content_DAL.get_template_contents(session)

	if template_contents is None or template_contents == False:
		raise not_found_exception("Template contents not found")

	return template_contents


@api_router.get("/template/template-contents/{template_id}/", tags=["template-contents"])
async def get_template_contents_by_template_id(template_id: str, auth: AuthJWT = Depends(),
                                               session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template_contents = await Template_Content_DAL.get_template_contents_by_template_id(user.id, template_id, session)

	if template_contents is None or template_contents == False:
		raise not_found_exception("Template contents not found")

	return template_contents


@api_router.get("/template-contents/{template_content_id}/", tags=["template-contents"])
async def get_template_content_by_template_content_id(template_content_id: str,
                                                      auth: AuthJWT = Depends(),
                                                      session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template_content = await Template_Content_DAL.get_template_content_by_template_content_id(user.id,
	                                                                                          template_content_id,
	                                                                                          session)

	if template_content is None or template_content == False:
		raise not_found_exception("Template content not found")

	return template_content


@api_router.post("/template-contents/", tags=["template-contents"])
async def create_template_content(created_template_content: Template_ContentSchema,
                                  auth: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = await Template_DAL.get_template_by_template_id(user.id, created_template_content.template_id,
	                                                          session)
	if template is None or template == False:
		raise not_found_exception("Template not found")

	template_content = await Template_Content_DAL.create_template_content(user.id, created_template_content, session)

	if template_content is None or template_content == False:
		raise not_found_exception("Template found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template content created successfully",
		                                              "body": jsonable_encoder(template_content)})
	except IntegrityError as ex:
		await session.rollback()
		raise incorrect_request_exception("Incorrect request")


@api_router.put("/template-contents/{template_content_id}/", tags=["template-contents"])
async def update_template_content(template_content_id: str, updated_template_content: Template_Content_UpdateSchema,
                                  auth: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template_content = await Template_Content_DAL.update_template_content(user.id, template_content_id,
	                                                                      updated_template_content,
	                                                                      session)

	if template_content is None or template_content == False:
		raise not_found_exception("Template content not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template content updated successfully",
		                                              "body": jsonable_encoder(template_content)})
	except IntegrityError as ex:
		await session.rollback()
		raise incorrect_request_exception("Incorrect request")


@api_router.delete("/template-contents/{template_content_id}/", tags=["template-contents"])
async def delete_template_content(template_content_id: str, auth: AuthJWT = Depends(),
                                  session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template_content = await Template_Content_DAL.delete_template_content(user.id, template_content_id, session)

	if template_content is None or template_content == False:
		raise not_found_exception("Template content not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template content deleted successfully",
		                                              "body": jsonable_encoder(template_content)})
	except IntegrityError as ex:
		await session.rollback()
		raise incorrect_request_exception("Incorrect request")
