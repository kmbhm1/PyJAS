from pydantic import ValidationError
from pydantic_core import ErrorDetails
from pyjas.v1_1.jsonapi_builder import (
    ALLOWED_JSONAPI_VERSIONS,
    JSONAPIObject,
)

import pytest


def clean_actual_errors(errors: list[ErrorDetails]) -> list[dict]:
    """Helper function to is_valid_uri up actual errors for comparison."""
    for e in errors:
        e.pop('ctx', None)  # Remove 'ctx' as it's not relevant for comparison
        e.pop('url', None)  # Remove 'url' as it's not relevant for comparison
    return errors


# JSONAPIObject tests


@pytest.mark.parametrize(
    'valid_data',
    [
        # Default version
        {},
        # Default version with meta
        {'meta': {'note': 'This is a JSON:API document.'}},
        # Specified allowed version '1.0'
        {'version': '1.0'},
        # Specified allowed version '1.1' explicitly
        {'version': '1.1'},
        # Version '1.0' with meta
        {'version': '1.0', 'meta': {'description': 'Version 1.0 of the API.'}},
        # Meta as empty dictionary
        {'meta': {}},
        # Combination of default version and meta
        {'meta': {'author': 'John Doe', 'contact': 'john.doe@example.com'}},
        # Meta with complex nested structures
        {
            'meta': {
                'analytics': {'page_views': 1000, 'unique_visitors': 800},
                'preferences': {'theme': 'dark', 'notifications': True},
            }
        },
    ],
)
def test_jsonapi_object_valid(valid_data):
    """Test that valid JSONAPIObject instances are created successfully."""
    try:
        obj = JSONAPIObject(**valid_data)

        # Assert 'version' is set correctly
        if 'version' in valid_data:
            assert obj.version == valid_data['version']
        else:
            assert obj.version == '1.1'  # Default value

        # Assert 'meta' is set correctly
        if 'meta' in valid_data:
            assert obj.meta == valid_data['meta']
        else:
            assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # 'version' not in allowed versions
        ({'version': '2.0'}, [f"JSONAPI 'version' must be one of {ALLOWED_JSONAPI_VERSIONS}."]),
        # 'version' with incorrect type (integer)
        ({'version': 1.1}, ['Input should be a valid string']),
        # 'version' as empty string
        ({'version': ''}, [f"JSONAPI 'version' must be one of {ALLOWED_JSONAPI_VERSIONS}."]),
        # 'meta' as non-dictionary (string)
        ({'meta': 'This should be a dict.'}, ['Input should be a valid dictionary']),
        # 'meta' as non-dictionary (list)
        ({'meta': ['not', 'a', 'dict']}, ['Input should be a valid dictionary']),
        # 'version' missing and no default (if default is not applied)
        # Assuming default is applied, this case may not be invalid
        # Including for completeness
        # (
        #     {},
        #     []  # No errors expected if default is applied
        # ),
        # 'version' as None (assuming it's not Optional)
        ({'version': None}, ['Input should be a valid string']),
    ],
)
def test_jsonapi_object_invalid(invalid_data, expected_error_messages):
    """Test that invalid JSONAPIObject instances raise ValidationError with correct messages."""
    with pytest.raises(ValidationError) as exc_info:
        JSONAPIObject(**invalid_data)

    # Extract actual errors
    actual_errors = exc_info.value.errors()

    # Flatten expected_error_messages if they are strings
    expected_errors = (
        expected_error_messages if isinstance(expected_error_messages, list) else [expected_error_messages]
    )

    for expected_error in expected_errors:
        # Check if any of the actual errors contain the expected error message
        assert any(
            expected_error in error['msg'] for error in actual_errors
        ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


@pytest.mark.parametrize(
    'valid_data',
    [
        # 'version' and 'meta' present
        {'version': '1.0', 'meta': {'additional': 'information'}},
        # 'version' present, 'meta' is None
        {'version': '1.1', 'meta': None},
        # Only 'version' present
        {'version': '1.1'},
        # 'meta' with various data types
        {'version': '1.0', 'meta': {'count': 10, 'active': True, 'items': ['item1', 'item2']}},
    ],
)
def test_jsonapi_object_optional_meta(valid_data):
    """Test that 'meta' field is optional and handles various valid scenarios."""
    try:
        obj = JSONAPIObject(**valid_data)

        # Assert 'version' is set correctly
        assert obj.version == valid_data['version']

        # Assert 'meta' is set correctly
        if 'meta' in valid_data:
            assert obj.meta == valid_data['meta']
        else:
            assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_meta_data, expected_error_messages',
    [
        # # 'meta' with unserializable data (set)
        # ({'version': '1.1', 'meta': {'unserializable': set([1, 2, 3])}}, ['Input should be a valid dictionary']),
        # 'meta' with invalid key types (non-string)
        ({'version': '1.1', 'meta': {123: 'numeric key'}}, ['Input should be a valid string']),
    ],
)
def test_jsonapi_object_invalid_meta(invalid_meta_data, expected_error_messages):
    """Test that invalid 'meta' field data raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        JSONAPIObject(**invalid_meta_data)

    actual_errors = exc_info.value.errors()
    expected_errors = (
        expected_error_messages if isinstance(expected_error_messages, list) else [expected_error_messages]
    )

    for expected_error in expected_errors:
        assert any(
            expected_error in error['msg'] for error in actual_errors
        ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_jsonapi_object_version_default():
    """Test that the default 'version' value is correctly set when not provided."""
    try:
        obj = JSONAPIObject()
        assert obj.version == '1.1'
        assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly when using default version: {e}')


def test_jsonapi_object_meta_none():
    """Test that 'meta' can be explicitly set to None."""
    try:
        obj = JSONAPIObject(meta=None)
        assert obj.version == '1.1'  # Default version
        assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'meta' is None: {e}")


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # 'version' as a list
        ({'version': ['1.1']}, ['Input should be a valid string']),
        # 'version' as a dictionary
        ({'version': {'major': 1, 'minor': 1}}, ['Input should be a valid string']),
        # 'meta' as integer
        ({'version': '1.1', 'meta': 123}, ['Input should be a valid dictionary']),
        # 'meta' as list
        ({'version': '1.1', 'meta': ['not', 'a', 'dict']}, ['Input should be a valid dictionary']),
    ],
)
def test_jsonapi_object_invalid_type_fields(invalid_data, expected_error_messages):
    """Test that 'version' and 'meta' fields enforce correct types."""
    with pytest.raises(ValidationError) as exc_info:
        JSONAPIObject(**invalid_data)

    actual_errors = exc_info.value.errors()
    expected_errors = (
        expected_error_messages if isinstance(expected_error_messages, list) else [expected_error_messages]
    )

    for expected_error in expected_errors:
        assert any(
            expected_error in error['msg'] for error in actual_errors
        ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"
