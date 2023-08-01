#!/usr/bin/env python

"""Tests for `dynamodb_mapping` package."""

import pytest

from dynamodb_mapping import DynamoDBMapping

TEST_TABLE_HASH_KEY_NAME = "test_primary_key"

TEST_ITEM1_KEY = "first_item"
TEST_ITEM1 = {TEST_TABLE_HASH_KEY_NAME: TEST_ITEM1_KEY, "foo": "bar"}

TEST_ITEM2_KEY = "second_item"
TEST_ITEM2 = {TEST_TABLE_HASH_KEY_NAME: TEST_ITEM2_KEY, "foo2": "bar2"}

TEST_ATTRIBUTES = {"foo": "bar"}


@pytest.fixture
def mapping(mocker):
    boto3_session = mocker.MagicMock()
    boto3_session.resource().Table().key_schema = [
        {"AttributeName": TEST_TABLE_HASH_KEY_NAME, "KeyType": "HASH"}
    ]
    return DynamoDBMapping("table_name", boto3_session=boto3_session)


def test_init(mapping):
    assert mapping.key_names == (TEST_TABLE_HASH_KEY_NAME,)


def test_scan(mapping, mocker):
    mapping.table.scan = mocker.MagicMock(return_value={"Items": [TEST_ITEM1]})
    assert next(mapping.scan()) == TEST_ITEM1


def test_scan_pages(mapping, mocker):
    mapping.table.scan = mocker.MagicMock(
        side_effect=[
            {"Items": [TEST_ITEM1], "LastEvaluatedKey": "to_be_continued"},
            {"Items": [TEST_ITEM2]},
        ]
    )
    results = mapping.scan()
    assert next(results) == TEST_ITEM1
    assert next(results) == TEST_ITEM2
    assert mapping.table.scan.call_count == 2


def test_get_item(mapping, mocker):
    mapping.table.get_item = mocker.MagicMock(return_value={"Item": TEST_ITEM1})
    assert mapping.get_item(TEST_ITEM1_KEY) == TEST_ITEM1
    mapping.table.get_item.assert_called_with(
        Key={TEST_TABLE_HASH_KEY_NAME: TEST_ITEM1_KEY}
    )


def test_invalid_keys(mapping):
    with pytest.raises(ValueError):
        mapping.get_item((TEST_ITEM1_KEY, TEST_ITEM2_KEY))


def test_get_item_non_existing(mapping, mocker):
    mapping.table.get_item = mocker.MagicMock(return_value={})
    with pytest.raises(KeyError):
        mapping.get_item(TEST_ITEM1_KEY)


def test_get_item_accessor(mapping, mocker):
    mapping.table.get_item = mocker.MagicMock(return_value={"Item": TEST_ITEM1})
    mapping.modify_item = mocker.MagicMock()
    accessor = mapping.get_item(TEST_ITEM1_KEY)
    mapping.table.get_item.assert_called_with(
        Key={TEST_TABLE_HASH_KEY_NAME: TEST_ITEM1_KEY}
    )
    accessor["new_attrib"] = "foobar"
    mapping.modify_item.assert_called_with(TEST_ITEM1_KEY, {"new_attrib": "foobar"})


def test_set_item(mapping, mocker):
    mapping.table.put_item = mocker.MagicMock()
    mapping.set_item(TEST_ITEM1_KEY, TEST_ATTRIBUTES)
    mapping.table.put_item.assert_called_with(
        Item={TEST_TABLE_HASH_KEY_NAME: TEST_ITEM1_KEY, **TEST_ATTRIBUTES}
    )


def test_put_item(mapping, mocker):
    mapping.set_item = mocker.MagicMock()
    mapping.put_item(TEST_ITEM1_KEY, TEST_ATTRIBUTES)
    mapping.set_item.assert_called_with(TEST_ITEM1_KEY, TEST_ATTRIBUTES)


def test_del_item(mapping, mocker):
    mapping.table.delete_item = mocker.MagicMock()
    mapping.del_item(TEST_ITEM1_KEY, check_existing=False)
    mapping.table.delete_item.assert_called_with(
        Key={TEST_TABLE_HASH_KEY_NAME: TEST_ITEM1_KEY}
    )


def test_del_item_non_existing(mapping, mocker):
    mapping.table.delete_item = mocker.MagicMock()
    mapping.keys = mocker.MagicMock(return_value=[TEST_ITEM2_KEY])
    with pytest.raises(KeyError):
        mapping.del_item(TEST_ITEM1_KEY)


def test_modify_item(mapping, mocker):
    mapping.table.update_item = mocker.MagicMock()
    mapping.modify_item(
        TEST_ITEM1_KEY, {"new1": "foobar!", "new2": "bar_foo!", "zombie": None}
    )
    mapping.table.update_item.assert_called_with(
        Key={TEST_TABLE_HASH_KEY_NAME: TEST_ITEM1_KEY},
        UpdateExpression="set #key0 = :value0, #key1 = :value1 remove #key2",
        ExpressionAttributeValues={":value0": "foobar!", ":value1": "bar_foo!"},
        ExpressionAttributeNames={"#key0": "new1", "#key1": "new2", "#key2": "zombie"},
    )


def test_modify_empty(mapping):
    with pytest.warns(UserWarning):
        mapping.modify_item(TEST_ITEM1_KEY, {})


def test_op_iter(mapping, mocker):
    mapping.scan = mocker.MagicMock(
        return_value=[
            {TEST_TABLE_HASH_KEY_NAME: TEST_ITEM1_KEY},
            {TEST_TABLE_HASH_KEY_NAME: TEST_ITEM2_KEY},
        ]
    )
    assert list(mapping) == [TEST_ITEM1_KEY, TEST_ITEM2_KEY]
    mapping.scan.assert_called_with(ProjectionExpression=TEST_TABLE_HASH_KEY_NAME)


def test_op_len(mapping):
    mapping.table.item_count = 42
    assert len(mapping) == 42


def test_op_getitem(mapping, mocker):
    mapping.get_item = mocker.MagicMock(return_value=TEST_ITEM1)
    assert mapping[TEST_ITEM1_KEY] == TEST_ITEM1
    mapping.get_item.assert_called_with(TEST_ITEM1_KEY)


def test_op_setitem(mapping, mocker):
    mapping.set_item = mocker.MagicMock()
    mapping[TEST_ITEM1_KEY] = TEST_ITEM1
    mapping.set_item.assert_called_with(TEST_ITEM1_KEY, TEST_ITEM1)


def test_op_delitem(mapping, mocker):
    mapping.del_item = mocker.MagicMock()
    del mapping[TEST_ITEM1_KEY]
    mapping.del_item.assert_called_with(TEST_ITEM1_KEY)


def test_items_view(mapping, mocker):
    mapping.scan = mocker.MagicMock(return_value=[TEST_ITEM1, TEST_ITEM2])
    items = mapping.items()
    assert list(items) == [(TEST_ITEM1_KEY, TEST_ITEM1), (TEST_ITEM2_KEY, TEST_ITEM2)]


def test_values_view(mapping, mocker):
    mapping.scan = mocker.MagicMock(return_value=[TEST_ITEM1])
    values = mapping.values()
    assert TEST_ITEM1 in values
    assert TEST_ITEM2 not in values
    assert list(values) == [TEST_ITEM1]


def test_keys_view(mapping, mocker):
    mapping.table.get_item = mocker.MagicMock(side_effect=[{"Item": TEST_ITEM1}])
    keys = mapping.keys()
    assert TEST_ITEM1_KEY in keys


def test_keys_view_non_existing(mapping, mocker):
    mapping.table.get_item = mocker.MagicMock(side_effect=[{}])
    keys = mapping.keys()
    assert TEST_ITEM1_KEY not in keys
