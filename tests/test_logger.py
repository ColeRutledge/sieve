import json
import logging
import sys

from datadog_api_client.v2.model.http_log import HTTPLog
from pytest import LogCaptureFixture, MonkeyPatch

from sieve.exceptions import SystemException
from sieve.logger import (
    DatadogHandler,
    JsonFormatter,
    RotatingFileHandler,
    StreamHandler,
    get_logger,
)


def test_get_logger_returns_expected_logging_config_for_testing(
    monkeypatch: MonkeyPatch,
    test_settings,
):
    monkeypatch.setattr("sieve.logger.settings", test_settings)
    logger = get_logger(__name__)

    for handler in logger.handlers:
        assert type(handler) in (StreamHandler, RotatingFileHandler)

    assert logger.propagate is True
    assert logger.level == logging.DEBUG
    assert logger.name == "tests.test_logger"


def test_get_logger_returns_expected_logging_config_for_prod(
    monkeypatch: MonkeyPatch,
    prod_settings,
):
    monkeypatch.setattr("sieve.logger.settings", prod_settings)
    logger = get_logger(__name__)

    for handler in logger.handlers:
        assert type(handler) in (StreamHandler, DatadogHandler)

    assert logger.propagate is True
    assert logger.level == logging.INFO
    assert logger.name == "tests.test_logger"


def test_datadog_and_stream_handlers_log_output(
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
    dev_settings,
    enable_logging,
):
    class MockLogsApi:
        def __init__(self, api_client):
            self.api_client = api_client

        def submit_log(self, body, *args, **kwargs):
            if '"level": "DEBUG"' in str(body):
                assert '"extra_attribute": true' in str(body)
            assert isinstance(body, HTTPLog)

    monkeypatch.setattr("sieve.logger.LogsApi", MockLogsApi)
    monkeypatch.setattr("sieve.logger.settings", dev_settings)
    monkeypatch.setattr("sieve.logger.DATADOG_CLIENT", "good_client")

    logger = get_logger(__name__)
    logger.debug("MESSAGE", extra={"extra_attribute": True})

    try:
        raise SystemException("ERROR")
    except SystemException:
        logger.exception("EXCEPTION", stack_info=True)

    assert "MESSAGE" in caplog.text
    assert "Traceback" in caplog.text
    assert "ERROR" in caplog.text
    assert "Stack (most recent call last)" in caplog.text


def test_datadog_env_var_warning(
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
    dev_settings,
    enable_logging,
):
    monkeypatch.setattr("sieve.logger.settings", dev_settings)
    monkeypatch.setattr("sieve.logger.settings.dd_api_key", None)
    monkeypatch.setattr("sieve.logger.settings.dd_site", None)
    get_logger(__name__)
    assert "* * * DD_API_KEY & DD_SITE REQUIRED" in caplog.text


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
        raise SystemException("BAD VALUE")
    except SystemException:
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
    assert 'SystemException("BAD VALUE")\nsieve.exceptions.SystemException: BAD VALUE' in traceback
    assert formatted_record == {
        "logger": {"name": "tests.test_logger", "thread_name": "MainThread"},
        "level": "ERROR",
        "message": "ERROR",
        "function_name": "test_json_formatter_parses_exception_payload_correctly",
        "exception_message": "BAD VALUE",
        "exception_type": "SystemException",
    }
