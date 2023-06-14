import datetime

from pocketbase.utils import camel_to_snake, to_datetime


def test_utils():
    assert camel_to_snake("TestCase") == "test_case"
    assert camel_to_snake("test_case") == "test_case"
    assert camel_to_snake("TestBS123") == "test_bs123"
    assert to_datetime("2022-01-31 12:01:05") == datetime.datetime(
        2022, 1, 31, 12, 1, 5
    )
    assert isinstance(to_datetime("2022-01-31"), str)
