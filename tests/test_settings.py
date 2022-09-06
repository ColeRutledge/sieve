# pylint: disable = import-outside-toplevel

import logging

from pydantic import SecretStr
from pytest import MonkeyPatch

from tests.conftest import MockSettings


def test_settings_defaults():
    settings = MockSettings()
    assert settings.dict() == {
        "app_env": "dev",
        "hostname": "localhost",
        "log_level": logging.DEBUG,
        "db_name": "sieve_db",
        "db_user": SecretStr("sieve_user"),
        "db_pass": SecretStr("pass"),
        "db_host": "db",
        "linkedin_email": None,
        "linkedin_pass": None,
        "dd_site": None,
        "dd_api_key": None,
        "app_name": "sieve",
        "driver_width": 1200,
        "driver_height": 800,
    }


def test_test_settings(monkeypatch: MonkeyPatch, test_settings: MockSettings):
    monkeypatch.setattr("sieve.settings.settings", test_settings)
    from sieve.settings import settings

    assert settings.dict() == {
        "app_env": "test",
        "log_level": logging.DEBUG,
        "hostname": "localhost",
        "linkedin_email": SecretStr("test_user"),
        "linkedin_pass": SecretStr("test_pass"),
        "db_name": "test_db",
        "db_user": SecretStr("test_user"),
        "db_pass": SecretStr("test_pass"),
        "db_host": "localhost",
        "dd_site": SecretStr("test.datadog.site"),
        "dd_api_key": SecretStr("test_api_key"),
        "app_name": "test_service",
        "driver_width": 1200,
        "driver_height": 800,
    }
    assert test_settings.is_dev is False
    assert test_settings.is_test is True
    assert test_settings.is_prod is False


def test_dev_settings(monkeypatch: MonkeyPatch, dev_settings: MockSettings):
    monkeypatch.setattr("sieve.settings.settings", dev_settings)
    from sieve.settings import settings

    assert settings.dict() == {
        "app_env": "dev",
        "log_level": logging.DEBUG,
        "hostname": "dev_host",
        "linkedin_email": SecretStr("dev_user"),
        "linkedin_pass": SecretStr("dev_pass"),
        "db_name": "dev_db",
        "db_user": SecretStr("dev_user"),
        "db_pass": SecretStr("dev_pass"),
        "db_host": "dev_host",
        "dd_site": SecretStr("dev.datadog.site"),
        "dd_api_key": SecretStr("dev_api_key"),
        "app_name": "dev_service",
        "driver_width": 1200,
        "driver_height": 800,
    }
    assert dev_settings.is_dev is True
    assert dev_settings.is_test is False
    assert dev_settings.is_prod is False


def test_prod_settings(monkeypatch: MonkeyPatch, prod_settings: MockSettings):
    monkeypatch.setattr("sieve.settings.settings", prod_settings)
    from sieve.settings import settings

    assert settings.dict() == {
        "app_env": "prod",
        "log_level": logging.INFO,
        "hostname": "prod_host",
        "linkedin_email": SecretStr("prod_user"),
        "linkedin_pass": SecretStr("prod_pass"),
        "db_name": "prod_db",
        "db_user": SecretStr("prod_user"),
        "db_pass": SecretStr("prod_pass"),
        "db_host": "prod_host",
        "dd_site": SecretStr("prod.datadog.site"),
        "dd_api_key": SecretStr("prod_api_key"),
        "app_name": "prod_service",
        "driver_width": 1200,
        "driver_height": 800,
    }
    assert prod_settings.is_dev is False
    assert prod_settings.is_test is False
    assert prod_settings.is_prod is True
