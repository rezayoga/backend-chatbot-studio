from . import templates_router
import logging
import uuid
from .schemas import Template as TemplateSchema
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from project.templates.models import Template
from project.database import SessionLocal
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
session = SessionLocal()


@templates_router.get("/create/")
async def create():
    logger.info("create() called")

    session.add(Template(id=uuid.uuid4(), template_name=uuid.uuid4()))
    session.commit()

    return JSONResponse(status_code=200, content={"message": "success"})


@templates_router.get("/read/", response_model=List[TemplateSchema])
async def read():
    logger.info("read() called")

    templates = session.query(Template).all()
    if templates is None:
        raise HTTPException(status_code=404, detail="Empty templates")
    return JSONResponse(status_code=200, content=jsonable_encoder(templates))
