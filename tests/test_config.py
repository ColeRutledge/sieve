import logging

from sieve import config


def test_test_config(set_test_config):
    env_vars = {k: v for k, v in vars(config).items() if k.isupper()}
    assert env_vars == {
        "ENVIRONMENT": "testing",
        "HOSTNAME": "localhost",
        "IS_TESTING": True,
        "IS_DEV": False,
        "IS_PROD": False,
        "LOG_LEVEL": logging.DEBUG,
        "LINKEDIN_EMAIL": "test_user",
        "LINKEDIN_PASS": "test_pass",
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_PASS": "test_pass",
        "DB_HOST": "localhost",
        "DD_SITE": "test.datadog.site",
        "DD_API_KEY": "test_api_key",
    }


def test_dev_config(set_dev_config):
    env_vars = {k: v for k, v in vars(config).items() if k.isupper()}
    assert env_vars == {
        "ENVIRONMENT": "development",
        "HOSTNAME": "dev_host",
        "IS_TESTING": False,
        "IS_DEV": True,
        "IS_PROD": False,
        "LOG_LEVEL": logging.DEBUG,
        "LINKEDIN_EMAIL": "dev_user",
        "LINKEDIN_PASS": "dev_pass",
        "DB_NAME": "dev_db",
        "DB_USER": "dev_user",
        "DB_PASS": "dev_pass",
        "DB_HOST": "localhost",
        "DD_SITE": "dev.datadog.site",
        "DD_API_KEY": "dev_api_key",
        "DRIVER_WIDTH": 1200,
        "DRIVER_HEIGHT": 800,
    }


def test_prod_config(set_prod_config):
    env_vars = {k: v for k, v in vars(config).items() if k.isupper()}
    assert env_vars == {
        "ENVIRONMENT": "production",
        "HOSTNAME": "prod_host",
        "IS_TESTING": False,
        "IS_DEV": False,
        "IS_PROD": True,
        "LOG_LEVEL": logging.INFO,
        "LINKEDIN_EMAIL": "prod_user",
        "LINKEDIN_PASS": "prod_pass",
        "DB_NAME": "prod_db",
        "DB_USER": "prod_user",
        "DB_PASS": "prod_pass",
        "DB_HOST": "remote_host",
        "DD_SITE": "prod.datadog.site",
        "DD_API_KEY": "prod_api_key",
        "DRIVER_WIDTH": 1200,
        "DRIVER_HEIGHT": 800,
    }
