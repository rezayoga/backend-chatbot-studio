from email.policy import default
from unicodedata import name
from project.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean, Integer, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    templates = relationship("Template", backref="template_owner")

    def __repr__(self):
        return f"{self.name} <{self.email}>"


class Template_Content(Base):
    __tablename__ = "template_contents"

    id = Column(GUID, primary_key=True)
    parent_id = Column(GUID, nullable=True, index=True)
    payload = Column(JSONB, nullable=True)
    option = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, default=func.now())
    template_id = Column(GUID, ForeignKey("templates.id"))

    def __repr__(self) -> str:
        return f"<Template: {self.id} -  {self.content} -  {self.option}>"


class Template(Base):
    __tablename__ = "templates"

    id = Column(GUID, primary_key=True)
    client = Column(String(128), nullable=True)
    channel = Column(String(128), nullable=True)
    channel_account_alias = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, default=func.now())
    template_name = Column(Text, nullable=False)
    division_id = Column(String(128), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    template_contents = relationship("Template_Content", backref="template_content")
    template_changelogs = relationship("Template_Changelog", backref="template_changelog")

    def __repr__(self) -> str:
        return f"<Template: {self.id} -  {self.content} -  {self.channel} -  {self.channel_account_alias}>"


class Template_Changelog(Base):
    __tablename__ = "template_changelogs"

    id = Column(GUID, primary_key=True)
    version = Column(String(128), nullable=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, default=func.now())
    action = Column(String(128), nullable=True)
    payload = Column(JSONB, nullable=True)
    template_id = Column(GUID, ForeignKey("templates.id"))

    def __repr__(self) -> str:
        return f"<Template: {self.id} -  {self.template_id} -  {self.user_id} -  {self.action}>"
