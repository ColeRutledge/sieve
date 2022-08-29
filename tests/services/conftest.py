from pytest import MonkeyPatch, fixture

from sieve.services.driver import init_driver


def mock_remote_init(self, **kwargs) -> None:
    for key, val in kwargs.items():
        setattr(self, key, val)


def mock_set_window_size(self, width, height) -> None:
    self.height = height
    self.width = width


@fixture(scope="function")
def dev_driver(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("sieve.services.driver.Driver.__init__", mock_remote_init)
    monkeypatch.setattr("sieve.services.driver.Driver.set_window_size", mock_set_window_size)
    monkeypatch.setattr("sieve.services.driver.Driver.POLL_INTERVAL", 0)
    monkeypatch.setattr("sieve.services.driver.Driver.WAIT_TIME_SECONDS", 0.1)
    monkeypatch.setattr("sieve.services.driver.config.IS_DEV", True)
    driver = init_driver()
    yield driver


@fixture(scope="function")
def prod_driver(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("sieve.services.driver.Driver.__init__", mock_remote_init)
    monkeypatch.setattr("sieve.services.driver.Driver.set_window_size", mock_set_window_size)
    monkeypatch.setattr("sieve.services.driver.Driver.POLL_INTERVAL", 0)
    monkeypatch.setattr("sieve.services.driver.Driver.WAIT_TIME_SECONDS", 0.1)
    monkeypatch.setattr("sieve.services.driver.config.IS_PROD", True)
    driver = init_driver()
    yield driver
