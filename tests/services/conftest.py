from pytest import MonkeyPatch, fixture

from sieve.services.driver import init_driver
from tests.mocks import MockRemote, MockSettings


@fixture(name="patch_driver")
def patch_driver_(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("sieve.services.driver.Remote", MockRemote)
    monkeypatch.setattr("sieve.services.driver.Driver.POLL_INTERVAL", 0)
    monkeypatch.setattr("sieve.services.driver.Driver.WAIT_TIME_SECONDS", 0.1)


@fixture
def dev_driver(monkeypatch: MonkeyPatch, dev_settings: MockSettings, patch_driver):
    monkeypatch.setattr("sieve.services.driver.settings", dev_settings)
    driver = init_driver()
    yield driver


@fixture
def prod_driver(monkeypatch: MonkeyPatch, prod_settings: MockSettings, patch_driver):
    monkeypatch.setattr("sieve.services.driver.settings", prod_settings)
    driver = init_driver()
    yield driver
