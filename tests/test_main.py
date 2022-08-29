from unittest.mock import Mock

from pytest import LogCaptureFixture, MonkeyPatch

from sieve.__main__ import main


def test_main(caplog: LogCaptureFixture, monkeypatch: MonkeyPatch, enable_logging):
    class MockDatadogLogClient:
        def close(self):
            pass

    mock_client = MockDatadogLogClient()
    # https://github.com/python/mypy/issues/2427#issuecomment-929688736
    mock_client.close = Mock()  # type: ignore
    monkeypatch.setattr("sieve.__main__.logger.propagate", True)
    monkeypatch.setattr("sieve.__main__.DATADOG_LOG_CLIENT", mock_client)

    main()

    assert "MESSAGE\n" in caplog.text
    mock_client.close.assert_called_once()
