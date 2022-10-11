from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from passlib.handlers.bcrypt import bcrypt
from .schemas import User as UserSchema, Template as TemplateSchema, Template_Update as Template_UpdateSchema, \
	Template_Content as Template_ContentSchema


###
# Data Access Layer (DAL) for all service endpoints
###

def get_password_hash(password: str):
	return bcrypt.hash(password)


def verify_password(plain_password, hashed_password):
	return bcrypt.verify(plain_password, hashed_password)


async def auth_user(username: str, password: str, session: AsyncSession) -> User:
	u = await session.execute(select(User).where(User.username == username))
	user = u.scalars().first()
	if not user:
		return False
	if not verify_password(password, user.hashed_password):
		return False
	return user


async def auth_user_by_user_id(user_id: int, session: AsyncSession) -> User:
	u = await session.execute(select(User).where(User.id == user_id))
	user = u.scalars().first()
	if not user:
		return False
	return user


async def get_users(session: AsyncSession) -> list[User]:
	users = await session.execute(select(User))
	return users.scalars().all()


def create_user(created_user: UserSchema, session: AsyncSession) -> User:
	user = User()
	user.username = created_user.username
	user.email = created_user.email
	user.name = created_user.name
	user.hashed_password = get_password_hash(created_user.password)
	user.is_active = True
	session.add(user)
	return user


async def get_templates(session: AsyncSession) -> list[Template]:
	templates = await session.execute(select(Template))
	return templates.scalars().all()


async def get_template_by_template_id(template_id: str, session: AsyncSession) -> Template:
	t = await session.execute(select(Template).where(Template.id == template_id))
	template = t.scalars().first()
	return template


async def get_template_by_user_id(user_id: int, session: AsyncSession) -> Template:
	t = await session.execute(select(Template).where(Template.owner_id == user_id))
	template = t.scalars().first()
	return template


def create_template(user_id: int, created_template: TemplateSchema, session: AsyncSession) -> Template:
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


async def update_template(user_id: int, template_id: int, updated_template: Template_UpdateSchema,
                          session: AsyncSession) -> Template:
	t = await session.execute(select(Template).where(Template.id == template_id).where(Template.owner_id == user_id))
	template = t.scalars().first()

	if not template:
		return False

	template.client = updated_template.client
	template.channel_account_alias = updated_template.channel_account_alias
	template.template_name = updated_template.template_name
	template.template_description = updated_template.template_description
	template.division_id = updated_template.division_id
	return template


async def delete_template(user_id: int, template_id: int, session: AsyncSession) -> Template:
	t = await session.execute(select(Template).where(Template.id == template_id).where(Template.owner_id == user_id))
	template = t.scalars().first()

	if not template:
		return False

	template.is_deleted = True
	return template


async def get_template_contents(session: AsyncSession) -> list[Template_Content]:
	template_contents = await session.query(Template_Content).all()
	return template_contents