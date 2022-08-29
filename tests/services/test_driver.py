from pytest import LogCaptureFixture, MonkeyPatch, fixture, raises
from selenium.common.exceptions import NoSuchElementException

from sieve.logger import get_logger
from sieve.services.driver import Driver, init_driver
from tests.services.conftest import mock_remote_init, mock_set_window_size


class MockElement:
    def __init__(self, text, *args, **kwargs):
        self.text = text

    def screenshot(self, filename: str) -> bool:
        return True


def test_driver_init_for_dev_config(monkeypatch: MonkeyPatch, set_dev_config):
    monkeypatch.setattr("sieve.services.driver.Driver.__init__", mock_remote_init)
    monkeypatch.setattr("sieve.services.driver.Driver.set_window_size", mock_set_window_size)

    driver = init_driver()

    assert hasattr(driver, "xpath")
    assert driver.command_executor == "http://localhost:3000/webdriver"


def test_driver_init_for_prod_config(monkeypatch: MonkeyPatch, set_prod_config):
    monkeypatch.setattr("sieve.services.driver.Driver.__init__", mock_remote_init)
    monkeypatch.setattr("sieve.services.driver.Driver.set_window_size", mock_set_window_size)

    driver = init_driver()

    assert hasattr(driver, "xpath")
    assert driver.command_executor == "http://browserless:3000/webdriver"


def test_driver_xpath_returns_single_web_element(
    dev_driver: Driver,
    monkeypatch: MonkeyPatch,
):
    def mock_find_elements(*arg, **kwargs):
        return [MockElement("mock xpath")]

    monkeypatch.setattr("sieve.services.driver.Remote.find_elements", mock_find_elements)

    element = dev_driver.xpath("//*[text()='mock xpath']")

    assert element.text == "mock xpath"


def test_driver_xpath_raises_exception_when_element_not_found_in_time(
    dev_driver: Driver,
    monkeypatch: MonkeyPatch,
):
    def mock_find_elements(*arg, **kwargs):
        return []

    monkeypatch.setattr("sieve.services.driver.Remote.find_elements", mock_find_elements)
    monkeypatch.setattr("sieve.services.driver.Driver.save_screenshot", lambda self, filename: None)

    with raises(NoSuchElementException) as exc:
        dev_driver.xpath("//*[text()='bad xpath']")

    assert "Message: No elements found: //*[text()='bad xpath']\n" == str(exc.value)


def test_driver_get_logs_request_url(
    dev_driver: Driver,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
    enable_logging,
):
    # logging.disable breaks pytest ouput capturing
    get_logger("sieve.services.driver")

    monkeypatch.setattr("sieve.services.driver.Remote.get", lambda self, url: None)

    dev_driver.get("https://test-url.test")

    assert "Driver request: https://test-url.test" in caplog.text


@fixture(scope="function", name="patch_save_screenshot")
def patch_save_screenshot_(monkeypatch: MonkeyPatch):
    def mock_execute_script(self, script):
        if "offsetWidth" in script:
            return 1920
        if "offsetHeight" in script:
            return 5000
        return None

    def mock_get_window_size(self):
        return {"width": 1200, "height": 800}

    monkeypatch.setattr("sieve.services.driver.Driver.execute_script", mock_execute_script)
    monkeypatch.setattr("sieve.services.driver.Driver.get_window_size", mock_get_window_size)
    monkeypatch.setattr("sieve.services.driver.Driver.set_window_size", mock_set_window_size)


def test_driver_save_screenshot_returns_true_on_success(
    dev_driver: Driver,
    monkeypatch: MonkeyPatch,
    patch_save_screenshot,
):
    def mock_find_elements(*arg, **kwargs):
        return [MockElement("body")]

    monkeypatch.setattr("sieve.services.driver.Remote.find_elements", mock_find_elements)

    assert dev_driver.get_window_size() == {"width": 1200, "height": 800}
    assert dev_driver.save_screenshot("test.png") is True
    assert dev_driver.get_window_size() == {"width": 1200, "height": 800}


def test_driver_save_screenshot_returns_false_on_exception(
    dev_driver: Driver,
    monkeypatch: MonkeyPatch,
    patch_save_screenshot,
):
    def mock_xpath(self, xpath):
        raise Exception("ERROR")

    monkeypatch.setattr("sieve.services.driver.Driver.xpath", mock_xpath)

    assert dev_driver.get_window_size() == {"width": 1200, "height": 800}
    assert not dev_driver.save_screenshot("test.png")
    assert dev_driver.get_window_size() == {"width": 1200, "height": 800}
