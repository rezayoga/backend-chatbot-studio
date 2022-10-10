from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from .models import *
from passlib.handlers.bcrypt import bcrypt


def get_password_hash(password: str):
	return bcrypt.hash(password)


def verify_password(plain_password, hashed_password):
	return bcrypt.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str, session: AsyncSession) -> User:
	user = await session.execute(select(User).where(User.username == username))
	u = user.scalars().first()
	if not u:
		return False
	if not verify_password(password, u.hashed_password):
		return False
	return u


async def get_users(session: AsyncSession) -> list[User]:
	users = await session.query(User).all()
	return users


async def get_templates(session: AsyncSession) -> list[Template]:
	templates = await session.query(Template).all()
	return templates


async def get_template_contents(session: AsyncSession) -> list[Template_Content]:
	template_contents = await session.query(Template_Content).all()
	return template_contents
