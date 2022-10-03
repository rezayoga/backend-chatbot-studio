import os
from functools import lru_cache


class BaseConfig:
    DATABASE_URL: str = "postgresql+psycopg2://reza:reza@localhost/db_chatbot_studio"
    DATABASE_CONNECT_DICT: dict = {}

    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://127.0.0.1:6379/0"


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

    config_name = "development"
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
