from pytest import LogCaptureFixture, MonkeyPatch, raises
from selenium.common.exceptions import NoSuchElementException

from sieve.exceptions import SystemException
from sieve.services.driver import DriverProtocol, init_driver
from tests.mocks import MockRemote


def test_driver_init_for_dev_config(monkeypatch: MonkeyPatch, dev_settings):
    monkeypatch.setattr("sieve.services.driver.settings", dev_settings)
    monkeypatch.setattr("sieve.services.driver.Remote", MockRemote)

    driver = init_driver()

    assert hasattr(driver, "element")
    assert hasattr(driver, "_driver")
    assert driver.driver.command_executor == "http://localhost:3000/webdriver"


def test_driver_init_for_prod_config(monkeypatch: MonkeyPatch, prod_settings):
    monkeypatch.setattr("sieve.services.driver.settings", prod_settings)
    monkeypatch.setattr("sieve.services.driver.Remote", MockRemote)

    driver = init_driver()

    assert hasattr(driver, "element")
    assert hasattr(driver, "_driver")
    assert driver.driver.command_executor == "http://browserless:3000/webdriver"


def test_driver_xpath_returns_single_web_element(dev_driver: DriverProtocol):
    element = dev_driver.element("//*[text()='mock xpath']")
    assert element.text == "mock xpath"


def test_driver_xpath_raises_exception_when_element_not_found_in_time(dev_driver: DriverProtocol):
    setattr(dev_driver.driver, "find_elements", lambda *args, **kwargs: [])
    setattr(dev_driver, "save_screenshot", lambda *args, **kwargs: True)

    with raises(NoSuchElementException) as exc:
        dev_driver.element("//*[text()='bad xpath']")

    assert "Message: No elements found: //*[text()='bad xpath']\n" == str(exc.value)


def test_driver_get_logs_request_url(
    dev_driver: DriverProtocol,
    caplog: LogCaptureFixture,
    enable_logging,
):
    dev_driver.get("https://test-url.test")
    dev_driver.quit()

    assert "[driver] GET: https://test-url" in caplog.text


def test_driver_save_screenshot_returns_true_on_success(dev_driver: DriverProtocol):
    assert dev_driver.driver.get_window_size() == {"width": 1200, "height": 800}
    assert dev_driver.save_screenshot("test.png") is True
    assert dev_driver.driver.get_window_size() == {"width": 1200, "height": 800}


def test_driver_save_screenshot_returns_false_on_exception(dev_driver: DriverProtocol):
    def mock_element(*args, **kwargs):
        raise SystemException("ERROR")

    setattr(dev_driver, "element", mock_element)

    assert dev_driver.driver.get_window_size() == {"width": 1200, "height": 800}
    assert not dev_driver.save_screenshot("test.png")
    assert dev_driver.driver.get_window_size() == {"width": 1200, "height": 800}
