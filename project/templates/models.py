from project.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Template_Content(Base):
    __tablename__ = "template_contents"

    id = Column(String(128), primary_key=True)
    parent_id = Column(String(128), nullable=False, index=True)
    content = Column(Text, nullable=True)
    payload = Column(JSONB, nullable=True)
    option = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, default=func.now())
    template_id = Column(String(128), ForeignKey("templates.id"))

    def __repr__(self) -> str:
        return f"<Template: {self.id} -  {self.content} -  {self.option}>"


class Template(Base):
    __tablename__ = "templates"

    id = Column(String(128), primary_key=True)
    client = Column(String(128), nullable=True)
    channel = Column(String(128), nullable=True)
    channel_account_alias = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, default=func.now())
    template_name = Column(Text, nullable=False)
    division_id = Column(String(128), nullable=True)
    template_contents = relationship("Template_Content", backref="template")

    def __repr__(self) -> str:
        return f"<Template: {self.id} -  {self.content} -  {self.channel} -  {self.channel_account_alias}>"
