""" Environment Variable Management """

import logging
import os


# NOTE: env variables must be all caps for tests to pass

ENVIRONMENT = os.environ.get("ENVIRONMENT") or "testing"
IS_TESTING = ENVIRONMENT == "testing"
IS_DEV = ENVIRONMENT == "development"
IS_PROD = ENVIRONMENT == "production"


if not IS_TESTING:
    LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL") or "DEBUG")
    HOSTNAME = os.environ.get("HOSTNAME") or "localhost"
    if ENVIRONMENT == "production":
        assert HOSTNAME != "localhost"

    # linkedin
    LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL")
    LINKEDIN_PASS = os.environ.get("LINKEDIN_PASS")

    # db
    DB_NAME = os.environ.get("DB_NAME") or "sieve_db"
    DB_USER = os.environ.get("DB_USER") or "sieve_user"
    DB_PASS = os.environ.get("DB_PASS") or "pass"
    DB_HOST = os.environ.get("DB_HOST") or "db"

    # datadog
    DD_SITE = os.environ.get("DD_SITE")
    DD_API_KEY = os.environ.get("DD_API_KEY")

    # browserless
    DRIVER_WIDTH = int(os.environ.get("DRIVER_WIDTH", 1200))
    DRIVER_HEIGHT = int(os.environ.get("DRIVER_HEIGHT", 800))

else:
    LOG_LEVEL = logging.DEBUG
    HOSTNAME = "localhost"

    # linkedin
    LINKEDIN_EMAIL = "test_user"
    LINKEDIN_PASS = "test_pass"

    # db
    DB_NAME = "test_db"
    DB_USER = "test_user"
    DB_PASS = "test_pass"
    DB_HOST = "localhost"

    # datadog
    DD_SITE = "test.datadog.site"
    DD_API_KEY = "test_api_key"

    # browserless
    DRIVER_WIDTH = 1200
    DRIVER_HEIGHT = 800
