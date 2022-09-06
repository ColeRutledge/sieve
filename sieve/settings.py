""" Environment Variable Management """

import logging

from typing import Literal

from pydantic import BaseSettings, SecretStr, validator


class Settings(BaseSettings):
    app_name: str = "sieve"
    app_env: str = "dev"
    hostname: str = "localhost"
    log_level: Literal[10, 20, 30, 40, 50] = 10

    # db
    db_name: str = "sieve_db"
    db_user: SecretStr = SecretStr("sieve_user")
    db_pass: SecretStr = SecretStr("pass")
    db_host: str = "db"

    # linkedin
    linkedin_email: SecretStr | None = None
    linkedin_pass: SecretStr | None = None

    # datadog
    dd_site: SecretStr | None = None
    dd_api_key: SecretStr | None = None

    # browserless
    driver_width: int = 1200
    driver_height: int = 800

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"

    @validator("log_level", pre=True)
    def convert_to_level_number(cls, v):
        # pylint: disable = no-self-argument
        if v in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            return logging.getLevelName(v)
        return v


settings = Settings()
