from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from project.database import Base


class User(Base):
	__tablename__ = "users"
	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
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


class Template(Base):
	__tablename__ = "templates"

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	client_id = Column(String, nullable=True)
	channel_id = Column(String, nullable=True)
	account_id = Column(String, nullable=True)
	account_alias = Column(String, nullable=True)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())
	template_name = Column(Text, nullable=False)
	template_description = Column(Text, nullable=True)
	division_id = Column(String(128), nullable=True)
	is_deleted = Column(Boolean, default=False)
	owner_id = Column(String(128), ForeignKey("users.id"))
	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	template_contents = relationship(
		"Template_Content", backref="template_content", cascade="all, delete-orphan")

	UniqueConstraint('template_name', 'client_id', 'channel_id', 'account_id', 'account_alias',
	                 name='unique_template_name')

	def __repr__(self) -> str:
		return f"<Template: {self.id} - {self.template_name} -  {self.template_description}>"


class Template_Content(Base):
	__tablename__ = "template_contents"

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	parent_ids = Column(JSONB, nullable=True)
	payloads = Column(JSONB, nullable=True)
	label = Column(Text, nullable=True)
	position = Column(JSONB, nullable=True)
	is_deleted = Column(Boolean, default=False)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())

	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	template_id = Column(String, ForeignKey("templates.id"))

	def __repr__(self) -> str:
		return f"<Template Content: {self.id} -  {self.payload} - {self.label} - {self.parent_ids}>"
