import time

from datetime import datetime, timedelta

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ChromeOptions, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from sieve import config
from sieve.logger import get_logger


logger = get_logger(__name__)


class Driver(Remote):
    POLL_INTERVAL = 1
    WAIT_TIME_SECONDS = 5

    def xpath(self, xpath: str) -> WebElement:
        timeout = datetime.now() + timedelta(seconds=self.WAIT_TIME_SECONDS)
        while datetime.now() < timeout:
            elements = self.find_elements(by=By.XPATH, value=xpath)
            if elements:
                return elements[0]
            time.sleep(self.POLL_INTERVAL)

        self.save_screenshot("ss.png")
        raise NoSuchElementException(f"No elements found: {xpath}")

    def get(self, url: str) -> None:
        logger.info("Driver request: %s", url)
        super().get(url)

    def save_screenshot(self, filename: str) -> bool:
        w, h = self.get_window_size().values()
        _w = self.execute_script("return document.body.offsetWidth")
        _h = self.execute_script("return document.body.offsetHeight")
        self.set_window_size(_w, min(_h, 12000))
        try:
            self.xpath("//body").screenshot(filename)
            return True
        except Exception:
            logger.exception("Error saving screenshot")
            return False
        finally:
            self.set_window_size(w, h)


DRIVER_BASE_CONFIG = {
    "headless": "--headless",
    "no_sandbox": "--no-sandbox",
    "log_level": "--log-level=3",
    "window_size": "--window-size=1920,12000",
    "dev_shm": "--disable-dev-shm-usage",
}


def init_driver(option_overrides: dict | None = None) -> Driver:
    # pylint: disable = expression-not-assigned

    options = DRIVER_BASE_CONFIG | (option_overrides or {})
    chrome_options = ChromeOptions()
    [chrome_options.add_argument(arg) for arg in options.values() if arg]

    if config.IS_DEV:
        logger.info("[development] creating driver")
        driver = Driver(
            command_executor="http://localhost:3000/webdriver",
            options=chrome_options,
        )

    else:
        logger.info("[production] creating driver")
        driver = Driver(
            command_executor="http://browserless:3000/webdriver",
            options=chrome_options,
        )

    driver.set_window_size(config.DRIVER_WIDTH, config.DRIVER_HEIGHT)
    return driver
