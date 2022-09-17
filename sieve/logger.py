import json
import logging
import os
import sys

from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler as _RotatingFileHandler
from types import SimpleNamespace
from typing import Any, TextIO

from datadog_api_client import Configuration, ThreadedApiClient
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem

from sieve.settings import settings


# set root logger level
logging.getLogger().setLevel(settings.log_level)


DATADOG_CLIENT = None


class DatadogHandler(logging.StreamHandler):
    # pylint: disable = global-statement

    def __init__(self, stream: TextIO | None = None):
        global DATADOG_CLIENT
        if all([not DATADOG_CLIENT, not settings.is_test, settings.dd_api_key, settings.dd_site]):
            DATADOG_CLIENT = ThreadedApiClient(Configuration())
        assert DATADOG_CLIENT, "INVALID DATADOG_CLIENT"
        super().__init__(stream=stream)
        self.setFormatter(JsonFormatter())

    def emit(self, record: logging.LogRecord) -> None:
        api = LogsApi(DATADOG_CLIENT)
        api.submit_log(
            body=HTTPLog(
                [
                    HTTPLogItem(
                        message=self.format(record),
                        hostname=settings.hostname,
                        service=settings.app_name,
                        ddsource="python",
                        ddtags=f"env:{settings.app_env}",
                    ),
                ]
            )
        )


class JsonFormatter(logging.Formatter):
    _RESERVED_ATTRIBUTES: set[str] = {
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
            "logger": {"name": record.name, "thread_name": record.threadName},
            "level": record.levelname,
            "message": record.getMessage(),
            "function_name": record.funcName,
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
        }

        # exception details
        if record.exc_info and not record.exc_text:
            # cache converted traceback in exc_text attribute for other handlers to use
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            payload["traceback"] = record.exc_text
            if isinstance(record.exc_info, tuple):
                payload["exception_message"] = str(record.exc_info[1])
                payload["exception_type"] = getattr(record.exc_info[0], "__name__", None)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        # extras
        for extra in record.__dict__.keys() - JsonFormatter._RESERVED_ATTRIBUTES:
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
    def __init__(self, stream: TextIO | None = None):
        super().__init__(stream=sys.stdout)
        self.setFormatter(StreamFormatter())


class RotatingFileHandler(_RotatingFileHandler):
    # pylint: disable = too-many-arguments
    def __init__(
        self,
        filename: str = "logs/debug.log",
        mode: str = "a",
        maxBytes: int = 1024 * 1024,
        backupCount: int = 2,
        encoding: str = "utf-8",
        delay: bool = False,
        errors: Any | None = None,
    ):
        super().__init__(
            filename,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            errors=errors,
        )
        self.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s.%(lineno)d: %(message)s")
        )


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


def add_color(message: str, color: str) -> str:
    return f"{color}{message}{COLOR.END}"


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(level or settings.log_level)
    logger.addHandler(StreamHandler())

    # datadog config
    if all([not settings.is_test, settings.dd_api_key, settings.dd_site]):
        logger.addHandler(DatadogHandler())
        return logger

    if not settings.is_test:
        logger.warning(
            "%s* * * DD_API_KEY & DD_SITE REQUIRED -> Using RotatingFileHandler * * *%s",
            COLOR.WARNING,
            COLOR.END,
        )

    os.makedirs("logs", exist_ok=True)
    logger.addHandler(RotatingFileHandler())
    return logger
