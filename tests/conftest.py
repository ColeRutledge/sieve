# from typing import Literal

import logging

from pytest import fixture

from tests.mocks import MockSettings


_test_settings = MockSettings(
    app_env="test",
    log_level="DEBUG",
    hostname="localhost",
    linkedin_email="test_user",
    linkedin_pass="test_pass",
    db_name="test_db",
    db_user="test_user",
    db_pass="test_pass",
    db_host="localhost",
    dd_site="test.datadog.site",
    dd_api_key="test_api_key",
    app_name="test_service",
    driver_width=1200,
    driver_height=800,
)

_dev_settings = MockSettings(
    app_env="dev",
    log_level="DEBUG",
    hostname="dev_host",
    linkedin_email="dev_user",
    linkedin_pass="dev_pass",
    db_name="dev_db",
    db_user="dev_user",
    db_pass="dev_pass",
    db_host="dev_host",
    dd_site="dev.datadog.site",
    dd_api_key="dev_api_key",
    app_name="dev_service",
    driver_width=1200,
    driver_height=800,
)

_prod_settings = MockSettings(
    app_env="prod",
    log_level="INFO",
    hostname="prod_host",
    linkedin_email="prod_user",
    linkedin_pass="prod_pass",
    db_name="prod_db",
    db_user="prod_user",
    db_pass="prod_pass",
    db_host="prod_host",
    dd_site="prod.datadog.site",
    dd_api_key="prod_api_key",
    app_name="prod_service",
    driver_width=1200,
    driver_height=800,
)


@fixture
def test_settings():
    yield _test_settings


@fixture
def dev_settings():
    yield _dev_settings


@fixture
def prod_settings():
    yield _prod_settings


@fixture(scope="function")
def enable_logging():
    logging.disable(logging.NOTSET)
    yield
    logging.disable(logging.CRITICAL)
