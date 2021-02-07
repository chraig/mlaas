# -*- coding: utf-8 -*-
import os
from time import perf_counter
from logging.config import dictConfig
from utils.data_dir import get_datadir


DEFAULT_DURATION_FORMAT = "{:.3f}"

DEFAULT_APP_NAME = "mlaas"
ENV_LOCALAPPDATA = ""
if os.name == 'nt':  # Windows
    ENV_LOCALAPPDATA = os.environ["LOCALAPPDATA"]
elif os.name == 'posix':
    ENV_LOCALAPPDATA = os.path.join(get_datadir())


def get_duration(begin_time: float, fmt_: str = DEFAULT_DURATION_FORMAT) -> str:
    """Return elapsed based on input timestamp as string."""
    now_ = perf_counter()
    return fmt_.format(now_ - begin_time)


def get_app_dir(basedir: str = ENV_LOCALAPPDATA, appname: str = DEFAULT_APP_NAME) -> str:
    """Returns mlaas appdata dir.
    """
    app_dir = os.path.join(basedir, appname)
    try:
        os.makedirs(app_dir)
    except FileExistsError:
        pass
    return app_dir


DEFAULT_APP_DIR = get_app_dir()
DEFAULT_LOGFILE_NAME = os.path.join(DEFAULT_APP_DIR, "{}.log".format(DEFAULT_APP_NAME))

dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            # (time) (threadname) (thread:id) (logger.level) (
            "format": "%(asctime)s - %(threadName)s | %(thread)d | %(levelname)-3.3s | %(name)-8.8s - %(message)s"
        },
    },
    "handlers": {"wsgi": {
        "class": "logging.StreamHandler",
        "stream": "ext://flask.logging.wsgi_errors_stream",
        "formatter": "default"
        },
        "myfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": DEFAULT_LOGFILE_NAME,
            "maxBytes": 1000000,  # bytes
            "backupCount": 10,  # number of files to rotate through
            "formatter": "default"
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["wsgi", "myfile"]
    }
})
