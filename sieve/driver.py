import time

from datetime import datetime, timedelta
from typing import Protocol, TypeVar

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ChromeOptions, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from sieve.logger import get_logger
from sieve.settings import settings


logger = get_logger(__name__)


class ElementProtocol(Protocol):
    @property
    def text(self) -> str:
        ...

    def screenshot(self, filename: str) -> bool:
        ...


class Element:
    def __init__(self, element: WebElement) -> None:
        self._element = element

    @property
    def text(self) -> str:
        return self._element.text

    def screenshot(self, filename: str) -> bool:
        return self._element.screenshot(filename)


T_co = TypeVar("T_co", covariant=True)


class DriverProtocol(Protocol[T_co]):
    @property
    def driver(self) -> T_co:
        ...

    def get(self, url: str) -> None:
        ...

    def element(self, xpath: str) -> ElementProtocol:
        ...

    def save_screenshot(self, filename: str) -> bool:
        ...

    def quit(self) -> None:
        ...


class Driver:
    POLL_INTERVAL = 1
    WAIT_TIME_SECONDS = 5

    DRIVER_BASE_CONFIG = {
        "headless": "--headless",
        "no_sandbox": "--no-sandbox",
        "log_level": "--log-level=3",
        "window_size": "--window-size=1920,12000",
        "dev_shm": "--disable-dev-shm-usage",
    }

    def __init__(self, driver: Remote) -> None:
        self._driver = driver

    @property
    def driver(self) -> Remote:
        return self._driver

    def get(self, url: str) -> None:
        """Make an HTTP GET request"""
        logger.info("[driver] GET: %s", url)
        self.driver.get(url=url)

    def element(self, xpath: str) -> Element:
        """Will return the first located `Element` that matches the `xpath`"""
        timeout = datetime.now() + timedelta(seconds=self.WAIT_TIME_SECONDS)
        while datetime.now() < timeout:
            elements = self._find_elements(xpath)
            if elements:
                return elements[0]
            time.sleep(self.POLL_INTERVAL)

        self.save_screenshot("ss.png")
        raise NoSuchElementException(f"No elements found: {xpath}")

    def _find_elements(self, xpath: str) -> list[Element]:
        elements = self.driver.find_elements(by=By.XPATH, value=xpath)
        return [Element(e) for e in elements]

    def save_screenshot(self, filename: str) -> bool:
        """Save a PNG screenshot of the browser viewport at max resolution"""
        w, h = self.driver.get_window_size().values()
        body_w = self.driver.execute_script("return document.body.offsetWidth")
        body_h = self.driver.execute_script("return document.body.offsetHeight")
        self.driver.set_window_size(body_w, min(body_h, 12000))
        try:
            self.element("//body").screenshot(filename)
            return True
        except Exception:
            logger.exception("Error saving screenshot")
            return False
        finally:
            self.driver.set_window_size(w, h)

    def quit(self) -> None:
        self.driver.quit()


def init_driver(option_overrides: dict | None = None) -> DriverProtocol:
    # pylint: disable = expression-not-assigned

    options = Driver.DRIVER_BASE_CONFIG | (option_overrides or {})
    chrome_options = ChromeOptions()
    [chrome_options.add_argument(arg) for arg in options.values() if arg]

    if settings.is_dev:
        logger.info("[driver] dev driver connecting")
        driver = Remote(
            command_executor="http://browserless:3000/webdriver",
            options=chrome_options,
        )

    else:
        logger.info("[driver] prod driver connecting")
        driver = Remote(
            command_executor="http://browserless:3000/webdriver",
            options=chrome_options,
        )

    driver.set_window_size(settings.driver_width, settings.driver_height)
    return Driver(driver)
