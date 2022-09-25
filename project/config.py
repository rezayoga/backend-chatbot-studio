import os
import pathlib
from functools import lru_cache


class BaseConfig:
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://reza:reza@host.docker.internal/db_chatbot_studio")
    DATABASE_CONNECT_DICT: dict = {}

    CELERY_BROKER_URL: str = os.environ.get(
        "CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")            # NEW
    CELERY_RESULT_BACKEND: str = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")    # NEW


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_name = os.environ.get("FASTAPI_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
