import logging
import logging.config

from bugsnag.handlers import BugsnagHandler


def configure_logging():
    logging_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s: %(levelname)s] [%(pathname)s:%(lineno)d] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "loggers": {
            "project": {
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(logging_dict)
    logger = logging.getLogger("uvicorn.access")
    logger.setLevel(logging.ERROR)

    handler = BugsnagHandler()
    # send only ERROR-level logs and above
    # handler.setLevel(logging.ERROR)
    # logger.addHandler(handler)

    logger.addHandler(handler)
