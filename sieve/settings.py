""" Environment Variable Management """

from typing import Literal

from pydantic import BaseSettings, SecretStr


LogLevelStr = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    app_name: str = "sieve"
    app_env: str = "dev"
    hostname: str = "localhost"
    log_level: LogLevelStr = "DEBUG"

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


settings = Settings()
