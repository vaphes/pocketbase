import pytest
from pocketbase import Client
from pocketbase.models.record import Record
from pocketbase.utils import camel_to_snake

class DummyClient:
    def __init__(self, auto_snake_case=True):
        self.auto_snake_case = auto_snake_case

class DummyRecord(Record):
    def __init__(self, data, client=None):
        self.client = client
        self.expand = {}
        self.load(data)

def test_camel_to_snake_enabled():
    assert camel_to_snake("TestCase") == "test_case"
    assert camel_to_snake("testCase") == "test_case"
    assert camel_to_snake("test_case") == "test_case"
    assert camel_to_snake("TestBS123") == "test_bs123"
    assert camel_to_snake("TestCase", enabled=False) == "TestCase"

def test_record_snake_case_enabled():
    client = DummyClient(auto_snake_case=True)
    data = {"myFieldName": "value", "anotherField": 42}
    record = DummyRecord(data, client=client)
    assert hasattr(record, "my_field_name")
    assert hasattr(record, "another_field")
    assert record.my_field_name == "value"
    assert record.another_field == 42

def test_record_snake_case_disabled():
    client = DummyClient(auto_snake_case=False)
    data = {"myFieldName": "value", "anotherField": 42}
    record = DummyRecord(data, client=client)
    assert hasattr(record, "myFieldName")
    assert hasattr(record, "anotherField")
    assert not hasattr(record, "my_field_name")
    assert not hasattr(record, "another_field")
    assert record.myFieldName == "value"
    assert record.anotherField == 42
