import pytest

from sieve.exceptions import SystemException


def test_system_exception():

    with pytest.raises(SystemException, match=r"^ERROR$") as exc:
        raise SystemException("ERROR")

    assert "ERROR" == str(exc.value)
    assert "ERROR" == exc.value.message
    assert exc.value.extra is None
