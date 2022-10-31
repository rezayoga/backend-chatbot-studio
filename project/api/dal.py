from typing import List, Union

from fastapi.encoders import jsonable_encoder
from passlib.handlers.bcrypt import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from .models import Template_Content
from .schemas import User as UserSchema, Template as TemplateSchema, Template_Update as Template_UpdateSchema, \
	Template_Content as Template_ContentSchema, Template_Content_Update as Template_Content_UpdateSchema


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
	async def auth_user(cls, username: str, password: str, session: AsyncSession) -> Union[bool, User]:
		u = await session.execute(select(User).where(User.username == username).where(User.is_active == True))
		user = u.scalars().first()
		if not user:
			return False
		if not verify_password(password, user.hashed_password):
			return False
		return user

	@classmethod
	async def auth_user_by_user_id(cls, user_id: int, session: AsyncSession) -> Union[bool, User]:
		u = await session.execute(select(User).where(User.id == user_id).where(User.is_active == True))
		user = u.scalars().first()
		if not user:
			return False
		return user

	@classmethod
	async def get_users(cls, session: AsyncSession) -> Union[bool, List[User]]:
		users = await session.execute(select(User))
		u = users.scalars().all()
		if not u:
			return False
		return u

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
	async def get_templates(cls, session: AsyncSession) -> Union[bool, List[Template]]:
		templates = await session.execute(select(Template))
		t = templates.scalars().all()
		if not t:
			return False
		return t

	@classmethod
	async def get_template_by_template_id(cls, user_id: str, template_id: str, session: AsyncSession) -> Union[
		bool, Template]:
		template = await session.execute(
			select(Template).where(Template.id == template_id).where(Template.owner_id == user_id).where(
				Template.is_deleted == False))
		t = template.scalars().first()
		if not t:
			return False
		return t

	@classmethod
	async def get_template_by_user_id(cls, user_id: int, session: AsyncSession) -> Union[bool, Template]:
		template = await session.execute(
			select(Template).where(Template.owner_id == user_id).where(Template.is_deleted == False))
		t = template.scalars().all()
		if not t:
			return False
		return t

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
	                          session: AsyncSession) -> Union[bool, Template]:
		template = await session.execute(select(Template).where(Template.id == template_id)
		                                 .where(Template.owner_id == user_id)
		                                 .where(Template.is_deleted == False))
		t = template.scalars().first()

		if not t:
			return False

		t.client = updated_template.client
		t.channel_account_alias = updated_template.channel_account_alias
		t.template_name = updated_template.template_name
		t.template_description = updated_template.template_description
		t.division_id = updated_template.division_id

		return t

	@classmethod
	async def delete_template(cls, user_id: int, template_id: int, session: AsyncSession) -> Union[bool, Template]:
		template = await session.execute(
			select(Template).where(Template.id == template_id).where(Template.owner_id == user_id)
			.where(Template.is_deleted == False))
		t = template.scalars().first()

		if not t:
			return False

		t.is_deleted = True
		return t


### Template Content services ###

class Template_Content_DAL:
	@classmethod
	async def get_template_contents(cls, session: AsyncSession) -> Union[bool, List[Template_Content]]:
		template_contents = await session.execute(select(Template_Content))
		tc = template_contents.scalars().all()

		if not tc:
			return False

		return tc

	@classmethod
	async def get_template_contents_by_template_id(cls, user_id: int, template_id: int,
	                                               session: AsyncSession) -> Union[bool, List[Template_Content]]:

		template = await session.execute(
			select(Template).where(Template.id == template_id).where(Template.owner_id == user_id)
			.where(Template.is_deleted == False))

		t = template.scalars().first()

		if not t:
			return False

		template_contents = await session.execute(
			select(Template_Content).where(Template_Content.template_id == t.id)
			.where(Template_Content.is_deleted == False))

		tc = template_contents.scalars().all()

		if not tc:
			return False

		return tc

	@classmethod
	async def get_template_content_by_template_content_id(cls, user_id: int, template_content_id: int,
	                                                      session: AsyncSession) -> Union[bool, Template_Content]:

		template_content = await session.execute(
			select(Template_Content).where(Template_Content.id == template_content_id)
			.where(Template_Content.is_deleted == False))

		tc = template_content.scalars().first()

		if not tc:
			return False

		template = await session.execute(
			select(Template).where(Template.id == tc.template_id).where(Template.owner_id == user_id)
			.where(Template.is_deleted == False))

		t = template.scalars().first()

		if not t:
			return False

		return tc

	@classmethod
	async def create_template_content(cls, user_id: int, created_template_content: Template_ContentSchema,
	                                  session: AsyncSession) -> Union[bool, Template_Content]:

		template = await session.execute(select(Template).where(Template.id == created_template_content.template_id)
		                                 .where(Template.owner_id == user_id)
		                                 .where(Template.is_deleted == False))
		t = template.scalars().first()

		if not t:
			return False

		for i in range(len(created_template_content.payloads)):
			created_template_content.payloads[i] = created_template_content.payloads[i].dict(exclude_unset=True,
			                                                                                 exclude_none=True)

		payloads = jsonable_encoder(created_template_content.payloads)
		template_content = Template_Content()
		template_content.template_id = created_template_content.template_id
		template_content.parent_ids = jsonable_encoder(created_template_content.parent_ids)
		template_content.payloads = payloads
		template_content.label = created_template_content.label
		template_content.position = jsonable_encoder(created_template_content.position)
		session.add(template_content)
		return template_content

	@classmethod
	async def update_template_content(cls, user_id: int, template_content_id: int,
	                                  updated_template_content: Template_Content_UpdateSchema,
	                                  session: AsyncSession) -> Union[bool, Template_Content]:

		template_content = await session.execute(
			select(Template_Content).where(Template_Content.id == template_content_id).where(
				Template_Content.is_deleted == False))

		tc = template_content.scalars().first()

		if not tc:
			return False

		template = await session.execute(
			select(Template).where(Template.id == tc.template_id).where(Template.owner_id == user_id)
			.where(Template.is_deleted == False))

		t = template.scalars().first()

		if not t:
			return False

		if len(updated_template_content.payloads) > 0:
			for i in range(len(updated_template_content.payloads)):
				updated_template_content.payloads[i] = updated_template_content.payloads[i].dict(exclude_unset=True,
				                                                                                 exclude_none=True)
			tc.payloads = jsonable_encoder(updated_template_content.payloads)
		if updated_template_content.parent_ids:
			tc.parent_ids = jsonable_encoder(updated_template_content.parent_ids)

		if updated_template_content.label:
			tc.label = updated_template_content.label

		if updated_template_content.position:
			tc.position = jsonable_encoder(updated_template_content.position)

		return tc

	@classmethod
	async def delete_template_content(cls, user_id: int, template_content_id: int,
	                                  session: AsyncSession) -> Union[bool, Template_Content]:
		template_content = await session.execute(
			select(Template_Content).where(Template_Content.id == template_content_id).where(
				Template_Content.is_deleted == False))

		tc = template_content.scalars().first()

		if not tc:
			return False

		template = await session.execute(
			select(Template).where(Template.id == tc.template_id).where(Template.owner_id == user_id)
			.where(Template.is_deleted == False))

		t = template.scalars().first()

		if not t:
			return False

		tc.is_deleted = True
		return tc
