# coding: utf-8
from sqlalchemy import Column, Enum, Integer, String, Text, ForeignKey, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from project.database import Base

metadata = Base.metadata


class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, autoincrement=True)
	email = Column(String, unique=True, index=True)
	username = Column(String, unique=True, index=True)
	name = Column(String, nullable=True)
	hashed_password = Column(String, nullable=True)
	is_active = Column(Boolean, default=True)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())
	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	templates = relationship("Template", backref="template_owner", cascade="all, delete-orphan")

	def __repr__(self):
		return f"{self.name} <{self.email}>"


class Block_Edges(Base):
	__tablename__ = 'block_edges'
	source_block_id = Column(String, ForeignKey('blocks.id'), primary_key=True)
	target_block_id = Column(String, ForeignKey('blocks.id'), primary_key=True)


class Content(Base):
	__tablename__ = 'contents'

	id = Column(String, primary_key=True, default=func.uuid_generate_v4())
	label = Column(String)
	payload = Column(JSONB(astext_type=Text()))
	type = Column(Enum('TEXT', 'IMAGE', 'VIDEO', 'AUDIO', 'DOCUMENT', 'LOCATION', 'CONTACTS', 'BUTTON', 'LIST',
	                   name='payload_types'))
	is_deleted = Column(Boolean, default=False)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())

	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	block_id = Column(String, ForeignKey("blocks.id"))


	def __repr__(self):
		return f"<Content: {self.id} - {self.label} -  {self.type}>"


class Block(Base):
	__tablename__ = 'blocks'

	id = Column(String, primary_key=True, default=func.uuid_generate_v4())
	label = Column(String)
	type = Column(Enum('START', 'INTENT', 'KEYWORD', 'REPLY', 'ACTION', 'FORM', name='block_types'))
	position_x = Column(Integer)
	position_y = Column(Integer)
	is_deleted = Column(Boolean, default=False)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())

	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	template_id = Column(String, ForeignKey("templates.id"))
	contents = relationship(
		"Content", backref="blocks", cascade="all, delete-orphan")

	def __repr__(self):
		return f"<Block: {self.id} - {self.label} -  {self.type}>"


class Template(Base):
	__tablename__ = 'templates'

	id = Column(String, primary_key=True, default=func.uuid_generate_v4())
	title = Column(String)
	description = Column(Text)
	language = Column(String)
	type = Column(Enum('SMART', 'BASIC', name='template_types'))
	owner_id = Column(Integer, ForeignKey("users.id"))
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())
	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	is_deleted = Column(Boolean, default=False)
	blocks = relationship(
		"Block", backref="templates", cascade="all, delete-orphan")

	def __repr__(self):
		return f"<Template: {self.id} - {self.title} -  {self.type}>"
