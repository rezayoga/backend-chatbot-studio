from typing import List, Union

from passlib.handlers.bcrypt import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
# from .models import Template_Content
from .schemas import User as UserSchema, Template as TemplateSchema, Block as BlockSchema


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
	def create_template(cls, user_id: int, created_template: TemplateSchema, session: AsyncSession) -> Template:
		template = Template()
		template.owner_id = user_id
		template.title = created_template.title
		template.description = created_template.description
		template.is_deleted = False
		template.language = created_template.language
		template.type = created_template.type
		session.add(template)
		return template

	@classmethod
	async def update_template(cls, user_id: int, template_id: str, updated_template: TemplateSchema,
	                          session: AsyncSession) -> Union[bool, Template]:
		template = await session.execute(select(Template).where(Template.id == template_id)
		                                 .where(Template.owner_id == user_id)
		                                 .where(Template.is_deleted == False))
		t = template.scalars().first()

		if not t:
			return False

		if updated_template.title:
			t.title = updated_template.title
		if updated_template.description:
			t.description = updated_template.description
		if updated_template.language:
			t.language = updated_template.language
		if updated_template.type:
			t.type = updated_template.type
		if updated_template.is_deleted:
			t.is_deleted = updated_template.is_deleted

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

	@classmethod
	async def get_template_by_template_id(cls, user_id: int, template_id: str, session: AsyncSession) -> Union[
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
	async def get_templates(cls, session: AsyncSession) -> Union[bool, List[Template]]:
		templates = await session.execute(select(Template))
		t = templates.scalars().all()
		if not t:
			return False
		return t


#

### Block services ###

class Block_DAL:

	@classmethod
	async def create_block(cls, user_id: int, created_block: BlockSchema, session: AsyncSession) -> Block:
		template = await session.execute(
			select(Template).where(Template.owner_id == user_id).where(Template.id == created_block.template_id)
			.where(Template.is_deleted == False))

		t = template.scalars().first()
		if not t:
			return False

		block = Block()
		block.label = created_block.label
		block.type = created_block.type
		block.position_x = created_block.position_x
		block.position_y = created_block.position_y
		block.is_deleted = created_block.is_deleted
		block.template_id = created_block.template_id
		session.add(block)
		return block

	@classmethod
	async def update_block(cls, block_id: str, updated_block: BlockSchema,
	                       session: AsyncSession) -> Union[bool, Block]:
		block = await session.execute(select(Block).where(Block.id == block_id)
		                              .where(Block.is_deleted == False))
		t = block.scalars().first()

		if not t:
			return False

		if updated_block.label:
			t.label = updated_block.label
		if updated_block.type:
			t.type = updated_block.type
		if updated_block.position_x:
			t.position_x = updated_block.position_x
		if updated_block.position_y:
			t.position_y = updated_block.position_y
		if updated_block.is_deleted:
			t.is_deleted = updated_block.is_deleted
		if updated_block.template_id:
			t.template_id = updated_block.template_id

		return t

	@classmethod
	async def delete_block(cls, user_id: int, block_id: int, session: AsyncSession) -> Union[bool, Block]:
		block = await session.execute(
			select(Block).where(Block.id == block_id)
			.where(Block.is_deleted == False))
		b = block.scalars().first()

		if not b:
			return False

		template = await session.execute(
			select(Template).where(Template.owner_id == user_id).where(Template.id == b.template_id)
			.where(Template.is_deleted == False))

		t = template.scalars().first()

		if not t:
			return False

		b.is_deleted = True
		return b

	@classmethod
	async def get_block_by_block_id(cls, user_id: int, block_id: str, session: AsyncSession) -> Union[
		bool, Block]:
		block = await session.execute(
			select(Block).where(Block.id == block_id).where(
				Block.is_deleted == False))
		b = block.scalars().first()
		if not b:
			return False

		template = await session.execute(
			select(Template).where(Template.owner_id == user_id).where(Template.id == b.template_id)
			.where(Template.is_deleted == False))

		t = template.scalars().first()

		if not t:
			return False

		return b

	@classmethod
	async def get_block_by_user_id(cls, user_id: int, session: AsyncSession) -> Union[bool, Block]:

		template = await session.execute(
			select(Template).where(Template.owner_id == user_id)
			.where(Template.is_deleted == False))

		t = template.scalars().all()

		block = await session.execute(
			select(Block).where(Block.templates == user_id).where(Block.is_deleted == False))
		b = block.scalars().all()
		if not b:
			return False

		if not t:
			return False

		return t

	@classmethod
	async def get_blocks(cls, session: AsyncSession) -> Union[bool, List[Block]]:
		blocks = await session.execute(select(Block))
		t = blocks.scalars().all()
		if not t:
			return False
		return t

#
#
#
#
# ### Template Content services ###
#
# class Template_Content_DAL:
# 	@classmethod
# 	async def get_template_contents(cls, session: AsyncSession) -> Union[bool, List[Template_Content]]:
# 		template_contents = await session.execute(select(Template_Content))
# 		tc = template_contents.scalars().all()
#
# 		if not tc:
# 			return False
#
# 		return tc
#
# 	@classmethod
# 	async def get_template_contents_by_template_id(cls, user_id: int, template_id: int,
# 	                                               session: AsyncSession) -> Union[bool, List[Template_Content]]:
#
# 		template = await session.execute(
# 			select(Template).where(Template.id == template_id).where(Template.owner_id == user_id)
# 			.where(Template.is_deleted == False))
#
# 		t = template.scalars().first()
#
# 		if not t:
# 			return False
#
# 		template_contents = await session.execute(
# 			select(Template_Content).where(Template_Content.template_id == t.id)
# 			.where(Template_Content.is_deleted == False))
#
# 		tc = template_contents.scalars().all()
#
# 		if not tc:
# 			return False
#
# 		return tc
#
# 	@classmethod
# 	async def get_template_content_by_template_content_id(cls, user_id: int, template_content_id: int,
# 	                                                      session: AsyncSession) -> Union[bool, Template_Content]:
#
# 		template_content = await session.execute(
# 			select(Template_Content).where(Template_Content.id == template_content_id)
# 			.where(Template_Content.is_deleted == False))
#
# 		tc = template_content.scalars().first()
#
# 		if not tc:
# 			return False
#
# 		template = await session.execute(
# 			select(Template).where(Template.id == tc.template_id).where(Template.owner_id == user_id)
# 			.where(Template.is_deleted == False))
#
# 		t = template.scalars().first()
#
# 		if not t:
# 			return False
#
# 		return tc
#
# 	@classmethod
# 	async def create_template_content(cls, user_id: int, created_template_content: Template_ContentSchema,
# 	                                  session: AsyncSession) -> Union[bool, Template_Content]:
#
# 		template = await session.execute(select(Template).where(Template.id == created_template_content.template_id)
# 		                                 .where(Template.owner_id == user_id)
# 		                                 .where(Template.is_deleted == False))
# 		t = template.scalars().first()
#
# 		if not t:
# 			return False
#
# 		for i in range(len(created_template_content.payloads)):
# 			created_template_content.payloads[i] = created_template_content.payloads[i].dict(exclude_unset=True,
# 			                                                                                 exclude_none=True)
#
# 		payloads = jsonable_encoder(created_template_content.payloads)
# 		template_content = Template_Content()
# 		template_content.template_id = created_template_content.template_id
# 		template_content.parent_ids = jsonable_encoder(created_template_content.parent_ids)
# 		template_content.payloads = payloads
# 		template_content.label = created_template_content.label
# 		template_content.position = jsonable_encoder(created_template_content.position)
# 		session.add(template_content)
# 		return template_content
#
# 	@classmethod
# 	async def update_template_content(cls, user_id: int, template_content_id: int,
# 	                                  updated_template_content: Template_Content_UpdateSchema,
# 	                                  session: AsyncSession) -> Union[bool, Template_Content]:
#
# 		template_content = await session.execute(
# 			select(Template_Content).where(Template_Content.id == template_content_id).where(
# 				Template_Content.is_deleted == False))
#
# 		tc = template_content.scalars().first()
#
# 		if not tc:
# 			return False
#
# 		template = await session.execute(
# 			select(Template).where(Template.id == tc.template_id).where(Template.owner_id == user_id)
# 			.where(Template.is_deleted == False))
#
# 		t = template.scalars().first()
#
# 		if not t:
# 			return False
#
# 		if updated_template_content is not None and updated_template_content.payloads:
# 			for i in range(len(updated_template_content.payloads)):
# 				updated_template_content.payloads[i] = updated_template_content.payloads[i].dict(exclude_unset=True,
# 				                                                                                 exclude_none=True)
# 			tc.payloads = jsonable_encoder(updated_template_content.payloads)
# 		if updated_template_content is not None and updated_template_content.parent_ids:
# 			tc.parent_ids = jsonable_encoder(updated_template_content.parent_ids)
#
# 		if updated_template_content is not None and updated_template_content.label:
# 			tc.label = updated_template_content.label
#
# 		if updated_template_content is not None and updated_template_content.position:
# 			tc.position = jsonable_encoder(updated_template_content.position)
#
# 		if updated_template_content is not None and updated_template_content.template_id:
# 			tc.template_id = updated_template_content.template_id
#
# 		return tc
#
# 	@classmethod
# 	async def delete_template_content(cls, user_id: int, template_content_id: int,
# 	                                  session: AsyncSession) -> Union[bool, Template_Content]:
# 		template_content = await session.execute(
# 			select(Template_Content).where(Template_Content.id == template_content_id).where(
# 				Template_Content.is_deleted == False))
#
# 		tc = template_content.scalars().first()
#
# 		if not tc:
# 			return False
#
# 		template = await session.execute(
# 			select(Template).where(Template.id == tc.template_id).where(Template.owner_id == user_id)
# 			.where(Template.is_deleted == False))
#
# 		t = template.scalars().first()
#
# 		if not t:
# 			return False
#
# 		tc.is_deleted = True
# 		return tc
