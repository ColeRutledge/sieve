from pydantic.env_settings import SettingsSourceCallable

from sieve.services.driver import DriverProtocol, ElementProtocol
from sieve.settings import Settings


class MockSettings(Settings):
    """Disables pydantic from sourcing the environment for tests"""

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return (init_settings,)


class MockWebElement:
    def __init__(self, text: str):
        self.text = text

    def screenshot(self, filename: str) -> bool:
        return True


class TestElement(ElementProtocol):
    def __init__(self, element: MockWebElement):
        self._element = element

    @property
    def text(self) -> str:
        return self._element.text

    def screenshot(self, filename: str) -> bool:
        return True


class MockRemote:
    def __init__(self, *, command_executor, options):
        self.command_executor = command_executor
        self.options = options
        self.width = 1920
        self.height = 12000

    def get(self, url: str) -> None:
        return None

    def set_window_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def find_elements(self, by: str, value: str) -> list[MockWebElement]:
        if "body" in value:
            return [MockWebElement("body")]
        return [MockWebElement("mock xpath")]

    def get_window_size(self, *args, **kwargs) -> dict[str, int]:
        return {"width": self.width, "height": self.height}

    def execute_script(self, script: str, *args, **kwargs):
        if "offsetWidth" in script:
            return 1920
        if "offsetHeight" in script:
            return 3000
        return None

    def quit(self) -> None:
        return None


class TestDriver(DriverProtocol):
    def __init__(self, driver: MockRemote):
        self._driver = driver

    @property
    def driver(self) -> MockRemote:
        return self._driver

    def get(self, url: str) -> None:
        return None

    def element(self, xpath: str) -> ElementProtocol:
        return TestElement(MockWebElement("mock xpath"))

    def save_screenshot(self, filename: str) -> bool:
        return True
