import logging

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from passlib.handlers.bcrypt import bcrypt
from .schemas import User as UserSchema, Template as TemplateSchema, Template_Update as Template_UpdateSchema, \
	Template_Content as Template_ContentSchema


###
# Data Access Layer (DAL) for all service endpoints
###

### Authentication & User services ###

def get_password_hash(password: str):
	return bcrypt.hash(password)


def verify_password(plain_password, hashed_password):
	return bcrypt.verify(plain_password, hashed_password)


class User_DAL:
	@classmethod
	async def auth_user(cls, username: str, password: str, session: AsyncSession) -> User:
		u = await session.execute(select(User).where(User.username == username).where(User.is_active == True))
		user = u.scalars().first()
		if not user:
			return False
		if not verify_password(password, user.hashed_password):
			return False
		return user

	@classmethod
	async def auth_user_by_user_id(cls, user_id: int, session: AsyncSession) -> User:
		u = await session.execute(select(User).where(User.id == user_id).where(User.is_active == True))
		user = u.scalars().first()
		if not user:
			return False
		return user

	@classmethod
	async def get_users(cls, session: AsyncSession) -> list[User]:
		users = await session.execute(select(User))
		return users.scalars().all()

	@classmethod
	def create_user(cls, created_user: UserSchema, session: AsyncSession) -> User:
		user = User()
		user.username = created_user.username
		user.email = created_user.email
		user.name = created_user.name
		user.hashed_password = get_password_hash(created_user.password)
		user.is_active = True
		session.add(user)
		return user


### Template services ###

class Template_DAL:
	@classmethod
	async def get_templates(cls, session: AsyncSession) -> list[Template]:
		templates = await session.execute(select(Template))
		if not templates:
			return False
		return templates.scalars().all()

	@classmethod
	async def get_template_by_template_id(cls, user_id: str, template_id: str, session: AsyncSession) -> Template:
		t = await session.execute(
			select(Template).where(Template.id == template_id).where(Template.owner_id == user_id).where(
				Template.is_deleted == False))
		template = t.scalars().first()
		if not template:
			return False
		return template

	@classmethod
	async def get_template_by_user_id(cls, user_id: int, session: AsyncSession) -> Template:
		t = await session.execute(
			select(Template).where(Template.owner_id == user_id).where(Template.is_deleted == False))
		template = t.scalars().all()
		if not template:
			return False
		return template

	@classmethod
	def create_template(cls, user_id: int, created_template: TemplateSchema, session: AsyncSession) -> Template:
		template = Template()
		template.owner_id = user_id
		template.client = created_template.client
		template.channel = created_template.channel
		template.channel_account_alias = created_template.channel_account_alias
		template.template_name = created_template.template_name
		template.template_description = created_template.template_description
		template.division_id = created_template.division_id
		session.add(template)
		return template

	@classmethod
	async def update_template(cls, user_id: int, template_id: int, updated_template: Template_UpdateSchema,
	                          session: AsyncSession) -> Template:
		t = await session.execute(select(Template).where(Template.id == template_id).where(Template.owner_id == user_id) \
		                          .where(Template.is_deleted == False))
		template = t.scalars().first()

		if not template:
			return False

		template.client = updated_template.client
		template.channel_account_alias = updated_template.channel_account_alias
		template.template_name = updated_template.template_name
		template.template_description = updated_template.template_description
		template.division_id = updated_template.division_id
		return template

	@classmethod
	async def delete_template(cls, user_id: int, template_id: int, session: AsyncSession) -> Template:
		t = await session.execute(select(Template).where(Template.id == template_id).where(Template.owner_id == user_id) \
		                          .where(Template.is_deleted == False))
		template = t.scalars().first()

		if not template:
			return False

		template.is_deleted = True
		return template


### Template Content services ###

class Template_Content_DAL:
	@classmethod
	async def get_template_contents(cls, session: AsyncSession) -> list[Template_Content]:
		template_contents = await session.execute(select(Template_Content))
		if not template_contents:
			return False

		return template_contents.scalars().all()

	@classmethod
	async def create_template_content(cls, created_template_content: Template_ContentSchema,
	                                  session: AsyncSession) -> Template_Content:

		logging.log(logging.INFO, f"create_template_content: {created_template_content} / {type(created_template_content.payloads)}")

		payloads = jsonable_encoder(created_template_content.payloads)
		template_content = Template_Content()
		template_content.template_id = created_template_content.template_id
		template_content.parent_ids = jsonable_encoder(created_template_content.parent_ids)
		template_content.payloads = payloads
		template_content.option = created_template_content.option
		template_content.option_label = created_template_content.option_label
		template_content.option_position = jsonable_encoder(created_template_content.option_position)
		session.add(template_content)
		return template_content
