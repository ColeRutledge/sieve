import json
import logging
import sys

from importlib import reload

from datadog_api_client import ThreadedApiClient
from datadog_api_client.v2.model.http_log import HTTPLog
from pytest import LogCaptureFixture, MonkeyPatch, raises

from sieve import logger as logger_
from sieve.logger import (
    DatadogHandler,
    JsonFormatter,
    RotatingFileHandler,
    StreamHandler,
    get_logger,
)


def test_get_logger_returns_expected_logging_config_for_testing(set_test_config):
    logger = get_logger(__name__)

    for handler in logger.handlers:
        assert type(handler) in (StreamHandler, RotatingFileHandler)

    assert logger.propagate is True
    assert logger.level == logging.DEBUG
    assert logger.name == "tests.test_logger"


def test_get_logger_returns_expected_logging_config_for_prod(
    monkeypatch: MonkeyPatch,
    set_prod_config,
):
    logger = get_logger(__name__)

    for handler in logger.handlers:
        assert type(handler) in (StreamHandler, DatadogHandler)

    assert logger.propagate is True
    assert logger.level == logging.INFO
    assert logger.name == "tests.test_logger"


def test_datadog_handler_raises_exception_with_invalid_datadog_client(
    monkeypatch: MonkeyPatch,
    set_dev_config,
):
    monkeypatch.setattr("sieve.logger.DATADOG_LOG_CLIENT", None)

    logger = get_logger(__name__)

    with raises(ValueError) as exc:
        logger.info("MESSAGE")

    assert "ThreadedApiClient cannot be None" == str(exc.value)


def test_datadog_and_stream_handlers_log_output(
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
    set_dev_config,
):
    class MockLogsApi:
        def __init__(self, api_client):
            self.api_client = api_client

        def submit_log(self, body, *args, **kwargs):
            if '"level": "DEBUG"' in str(body):
                assert '"extra_attribute": true' in str(body)
            assert isinstance(body, HTTPLog)

    monkeypatch.setattr("sieve.logger.LogsApi", MockLogsApi)
    monkeypatch.setattr("sieve.logger.DATADOG_LOG_CLIENT", "good_client")

    logger = get_logger(__name__)
    logger.debug("MESSAGE", extra={"extra_attribute": True})

    try:
        raise Exception("ERROR")
    except Exception:
        logger.exception("EXCEPTION", stack_info=True)

    assert "MESSAGE" in caplog.text
    assert "Traceback" in caplog.text
    assert "ERROR" in caplog.text
    assert "Stack (most recent call last)" in caplog.text


def test_datadog_env_var_warning(
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
    set_dev_config,
):
    monkeypatch.setattr("sieve.logger.config.DD_API_KEY", None)
    monkeypatch.setattr("sieve.logger.config.DD_SITE", None)
    get_logger(__name__)
    assert "* * * DD_API_KEY & DD_SITE required" in caplog.text


def test_datadog_api_log_client_creation(set_dev_config):
    reload(logger_)
    assert isinstance(logger_.DATADOG_LOG_CLIENT, ThreadedApiClient)


def test_json_formatter_parses_debug_payload_correctly():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        **{
            "name": "tests.test_logger",
            "level": 10,
            "pathname": "sieve/tests/test_logger.py",
            "lineno": 100,
            "msg": "MESSAGE",
            "args": [],
            "exc_info": None,
            "func": "test_json_formatter_parses_debug_payload_correctly",
            "stack_info": None,
        }
    )
    formatted_record = json.loads(formatter.format(record))
    formatted_record.pop("timestamp")
    assert formatted_record == {
        "logger": {"name": "tests.test_logger", "thread_name": "MainThread"},
        "level": "DEBUG",
        "message": "MESSAGE",
        "function_name": "test_json_formatter_parses_debug_payload_correctly",
    }


def test_json_formatter_parses_exception_payload_correctly():
    exception_info = None
    try:
        raise ValueError("BAD VALUE")
    except ValueError:
        exception_info = sys.exc_info()

    formatter = JsonFormatter()
    record = logging.LogRecord(
        **{
            "name": "tests.test_logger",
            "level": 40,
            "pathname": "sieve/tests/test_logger.py",
            "lineno": 100,
            "msg": "ERROR",
            "args": [],
            "exc_info": exception_info,
            "func": "test_json_formatter_parses_exception_payload_correctly",
            "stack_info": None,
        }
    )
    formatted_record = json.loads(formatter.format(record))
    formatted_record.pop("timestamp")
    traceback = formatted_record.pop("traceback")
    assert 'raise ValueError("BAD VALUE")\nValueError: BAD VALUE' in traceback
    assert formatted_record == {
        "logger": {"name": "tests.test_logger", "thread_name": "MainThread"},
        "level": "ERROR",
        "message": "ERROR",
        "function_name": "test_json_formatter_parses_exception_payload_correctly",
        "exception_message": "BAD VALUE",
        "exception_type": "ValueError",
    }
