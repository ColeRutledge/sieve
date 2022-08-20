from importlib import reload

from pytest import MonkeyPatch, fixture

from sieve import config


@fixture(scope="function")
def set_test_config(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ENVIRONMENT", "testing")
    reload(config)
    yield
    monkeypatch.setenv("ENVIRONMENT", "testing")
    reload(config)


@fixture(scope="function")
def set_dev_config(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("HOSTNAME", "dev_host")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LINKEDIN_EMAIL", "dev_user")
    monkeypatch.setenv("LINKEDIN_PASS", "dev_pass")
    monkeypatch.setenv("DB_NAME", "dev_db")
    monkeypatch.setenv("DB_USER", "dev_user")
    monkeypatch.setenv("DB_PASS", "dev_pass")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DD_SITE", "dev.datadog.site")
    monkeypatch.setenv("DD_API_KEY", "dev_api_key")
    reload(config)
    yield
    monkeypatch.setenv("ENVIRONMENT", "testing")
    reload(config)


@fixture(scope="function")
def set_prod_config(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("HOSTNAME", "prod_host")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("LINKEDIN_EMAIL", "prod_user")
    monkeypatch.setenv("LINKEDIN_PASS", "prod_pass")
    monkeypatch.setenv("DB_NAME", "prod_db")
    monkeypatch.setenv("DB_USER", "prod_user")
    monkeypatch.setenv("DB_PASS", "prod_pass")
    monkeypatch.setenv("DB_HOST", "remote_host")
    monkeypatch.setenv("DD_SITE", "prod.datadog.site")
    monkeypatch.setenv("DD_API_KEY", "prod_api_key")
    reload(config)
    yield
    monkeypatch.setenv("ENVIRONMENT", "testing")
    reload(config)
