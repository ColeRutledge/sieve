import json
import logging
import os
import sys

from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler as _RotatingFileHandler
from types import SimpleNamespace
from typing import Any

from datadog_api_client import Configuration
from datadog_api_client import ThreadedApiClient as _ThreadedApiClient
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem

from sieve import config


COLOR = SimpleNamespace(
    HEADER="\033[95m",
    OKBLUE="\033[94m",
    OKCYAN="\033[96m",
    OKGREEN="\033[92m",
    WARNING="\033[93m",
    FAIL="\033[91m",
    END="\033[0m",
    BOLD="\033[1m",
    UNDERLINE="\033[4m",
    PURPLE="\033[35m",
    WHITE="\033[1;37m",
)


def add_color(message: str, color):
    return f"{color}{message}{COLOR.END}"


class DatadogHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(JsonFormatter())

    def emit(self, record: logging.LogRecord) -> None:
        if not DATADOG_LOG_CLIENT:
            raise ValueError("ThreadedApiClient cannot be None")
        api_instance = LogsApi(DATADOG_LOG_CLIENT)
        api_instance.submit_log(
            body=HTTPLog(
                [
                    HTTPLogItem(
                        message=self.format(record),
                        hostname=config.HOSTNAME,
                        service="sieve",
                        ddsource="python",
                        ddtags=f"env:{config.ENVIRONMENT}",
                    ),
                ]
            )
        )


class JsonFormatter(logging.Formatter):
    RESERVED_ATTRIBUTES: set[str] = {
        "name",
        "msg",
        "message",
        "args",
        "asctime",
        "level",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "function_name",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "timestamp",
        "processName",
        "process",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format `logging.LogRecord` into Datadog compatible payload"""

        payload: dict[str, Any] = {
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "function_name": record.funcName,
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
        }

        # exception details
        if record.exc_info and not record.exc_text:
            # cache the converted traceback in the exc_text attribute for other handlers
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            payload["exc_info"] = record.exc_text
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        # extras
        for extra in record.__dict__.keys() - JsonFormatter.RESERVED_ATTRIBUTES:
            payload[extra] = getattr(record, extra)

        return json.dumps(payload)


class StreamFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()

        level_name = add_color(f"[{record.levelname}]", COLOR.WARNING)

        record.asctime = self.formatTime(record, self.datefmt)
        time = add_color(record.asctime, COLOR.PURPLE)

        location = f"{record.name}.{record.lineno}"
        if len(location) < 30:
            location = f"{location:30}"
        location = add_color(location, COLOR.OKBLUE)

        log_message = f"{time:35} {level_name:20} {location} {message}"

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            log_message += add_color(f"\n{record.exc_text}", COLOR.FAIL)
        if record.stack_info:
            log_message += f"\n{self.formatStack(record.stack_info)}"

        return log_message


class StreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(stream=sys.stdout, *args, **kwargs)
        self.setFormatter(StreamFormatter())


class RotatingFileHandler(_RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(
            filename="logs/debug.log",
            maxBytes=1024 * 1024,
            encoding="utf-8",
            backupCount=2,
            *args,
            **kwargs,
        )
        self.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s.%(lineno)d: %(message)s")
        )


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(config.LOG_LEVEL)
    logger.addHandler(StreamHandler())

    # datadog config
    if config.ENVIRONMENT != "testing":
        if config.DD_API_KEY and config.DD_SITE:
            logger.addHandler(DatadogHandler())
            return logger

        logger.warning(
            "%s* * * DD_API_KEY & DD_SITE required -> using default handler * * *%s",
            COLOR.WARNING,
            COLOR.END,
        )

    logger.addHandler(RotatingFileHandler())
    return logger


# make logs dir
os.makedirs("logs", exist_ok=True)

# set root logger level
logging.getLogger().setLevel(config.LOG_LEVEL)

# configure datadog api client
DATADOG_LOG_CLIENT = None
if config.ENVIRONMENT != "testing":
    if config.DD_API_KEY and config.DD_SITE:
        configuration = Configuration()
        DATADOG_LOG_CLIENT = _ThreadedApiClient(configuration)
