from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from passlib.handlers.bcrypt import bcrypt


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


async def get_users(session: AsyncSession) -> list[User]:
	users = await session.execute(select(User))
	return users.scalars().all()


async def get_templates(session: AsyncSession) -> list[Template]:
	templates = await session.query(Template).all()
	return templates


async def get_template_contents(session: AsyncSession) -> list[Template_Content]:
	template_contents = await session.query(Template_Content).all()
	return template_contents
