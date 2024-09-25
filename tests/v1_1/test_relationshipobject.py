from pydantic import ValidationError
from pydantic_core import ErrorDetails
from pyjas.v1_1.jsonapi_builder import (
    ResourceIdentifierObject,
    LinkObject,
    RelationshipObject,
)

import pytest


def clean_actual_errors(errors: list[ErrorDetails]) -> list[dict]:
    """Helper function to is_valid_uri up actual errors for comparison."""
    for e in errors:
        e.pop('ctx', None)  # Remove 'ctx' as it's not relevant for comparison
        e.pop('url', None)  # Remove 'url' as it's not relevant for comparison
    return errors


@pytest.mark.parametrize(
    'valid_data',
    [
        # Only 'links'
        {
            'links': {
                'self': 'https://example.com/resource/1',
                'related': 'https://example.com/resource/1/related',
                'describedby': 'https://example.com/schema/resource',
            }
        },
        # 'links' with LinkObject instances
        {
            'links': {
                'self': LinkObject(href='https://example.com/resource/2', rel='self', title='Self Link'),
                'related': 'https://example.com/resource/2/related',
            }
        },
        # Only 'data' with single ResourceIdentifierObject
        {'data': ResourceIdentifierObject(type='articles', id='1')},
        # Only 'data' with list of ResourceIdentifierObject
        {
            'data': [
                ResourceIdentifierObject(type='comments', id='5'),
                ResourceIdentifierObject(type='comments', lid='local-123'),
            ]
        },
        # Only 'meta'
        {'meta': {'description': 'A relationship meta information', 'count': 10}},
        # Combination of 'links' and 'data'
        {
            'links': {'self': 'https://example.com/resource/3'},
            'data': ResourceIdentifierObject(type='posts', id='10'),
        },
        # Combination of 'links' and 'meta'
        {'links': {'self': 'https://example.com/resource/4'}, 'meta': {'note': 'Additional meta information'}},
        # Combination of 'data' and 'meta'
        {'data': [ResourceIdentifierObject(type='tags', id='2')], 'meta': {'usage': 'Primary tags'}},
        # All fields present
        {
            'links': {'self': 'https://example.com/resource/5', 'related': 'https://example.com/resource/5/related'},
            'data': [
                ResourceIdentifierObject(type='authors', id='3'),
                ResourceIdentifierObject(type='authors', lid='local-456'),
            ],
            'meta': {'summary': 'Relationship with all fields'},
        },
        # Extra members with valid names
        {'links': {'self': 'https://example.com/resource/7'}, 'additional_info': 'Some extra information'},
        # 'links' with None values
        {'links': {'self': None, 'related': 'https://example.com/resource/7/related'}},
        # 'data' as None with 'links' present
        {'links': {'self': 'https://example.com/resource/8'}, 'data': None},
        # 'links' with LinkObject containing all fields
        {
            'links': {
                'self': LinkObject(
                    href='https://example.com/resource/10',
                    rel='self',
                    describedby='https://example.com/schema/resource',
                    title='Self Link',
                    type='application/json',
                    hreflang='en',
                    meta={'source': 'internal'},
                )
            }
        },
    ],
)
def test_relationship_object_valid(valid_data):
    """Test that valid RelationshipObject instances are created successfully."""
    try:
        obj = RelationshipObject(**{**valid_data})
        # Check presence of fields
        if 'links' in valid_data:
            assert obj.links == valid_data['links']
        if 'data' in valid_data:
            assert obj.data == valid_data['data']
        if 'meta' in valid_data:
            assert obj.meta == valid_data['meta']
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # Missing all of 'links', 'data', 'meta'
        ({}, ["Value error, RelationshipObject must contain at least one of 'links', 'data', or 'meta'."]),
        # 'links' with invalid value type
        (
            {
                'links': {
                    'self': 12345  # Invalid type
                }
            },
            ['Input should be a valid string'],
        ),
        # 'links' with invalid URI string
        ({'links': {'self': 'not-a-valid-uri'}}, ["Value error, Link 'self' must be a valid URI-reference."]),
        # 'data' as invalid type (not ResourceIdentifierObject or list)
        (
            {'data': 'invalid-data'},
            ['Input should be a valid dictionary or instance of ResourceIdentifierObject'],
        ),
        # 'data' as list with invalid items
        (
            {'data': ['invalid-item', ResourceIdentifierObject(type='comments', id='5')]},
            ['Input should be a valid dictionary or instance of ResourceIdentifierObject'],
        ),
        # 'meta' as non-dictionary
        ({'meta': 'not-a-dict'}, ['Input should be a valid dictionary']),
        # Extra members with invalid names
        (
            {'links': {'self': 'https://example.com/resource/3'}, 'invalid_member!': 'Some value'},
            ["Invalid member name 'invalid_member!' according to JSON:API specification."],
        ),
        # 'hreflang' as unsupported type
        (
            {'hreflang': {'lang': 'en'}},
            ["Value error, RelationshipObject must contain at least one of 'links', 'data', or 'meta'."],
        ),
        # 'hreflang' as list containing non-string
        (
            {'hreflang': ['en', 123]},
            ["Value error, RelationshipObject must contain at least one of 'links', 'data', or 'meta'."],
        ),
        # 'hreflang' as list containing invalid language tag
        (
            {'hreflang': ['en', 'invalid-lang-tag']},
            ["Value error, RelationshipObject must contain at least one of 'links', 'data', or 'meta'."],
        ),
        # 'data' as empty list (assuming it's invalid if empty)
        ({'data': []}, ["Value error, RelationshipObject must contain at least one of 'links', 'data', or 'meta'."]),
        # 'meta' as empty dict
        ({'meta': {}}, ["Value error, RelationshipObject must contain at least one of 'links', 'data', or 'meta'."]),
        # 'data' as empty list
        ({'data': []}, ["Value error, RelationshipObject must contain at least one of 'links', 'data', or 'meta'."]),
        # 'links' with empty dict
        ({'links': {}}, ["Value error, RelationshipObject must contain at least one of 'links', 'data', or 'meta'."]),
    ],
)
def test_relationship_object_invalid(invalid_data, expected_error_messages):
    """Test that invalid RelationshipObject instances raise ValidationError with correct messages."""
    with pytest.raises(ValidationError) as exc_info:
        RelationshipObject(**invalid_data)

    # Extract actual errors
    actual_errors = clean_actual_errors(exc_info.value.errors())

    # Flatten expected_error_messages if they are strings
    expected_error = (
        expected_error_messages[0] if isinstance(expected_error_messages, list) else expected_error_messages
    )

    # Check if any of the actual errors contain the expected error message
    for expected_error in expected_error_messages:
        print(expected_error)
        print(actual_errors[0]['msg'])
        print(bool(expected_error == actual_errors[0]['msg']))
    assert any(
        expected_error in e['msg'] for e in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors' msg values for {actual_errors[0]['msg']}"


@pytest.mark.parametrize(
    'valid_data',
    [
        # 'links' with allowed extra fields
        {
            'links': {'self': 'https://example.com/resource/5', 'related': 'https://example.com/resource/5/custom'},
            'data': ResourceIdentifierObject(type='articles', id='10'),
            'meta': {'extra_info': 'Additional data'},
            'additional_member': 'Extra value',  # Extra member
        },
        # Multiple extra members with valid names
        {'links': {'self': 'https://example.com/resource/6'}, 'describedby': 'Value1', 'related': 'Value2'},
    ],
)
def test_relationship_object_with_extra_members(valid_data):
    """Test that RelationshipObject accepts extra members with valid names."""
    try:
        obj = RelationshipObject(**valid_data)
        # Verify known fields
        if 'links' in valid_data:
            assert obj.links == valid_data['links']
        if 'data' in valid_data:
            assert obj.data == valid_data['data']
        if 'meta' in valid_data:
            assert obj.meta == valid_data['meta']

        # Verify extra members
        extra_members = set(valid_data.keys()) - {'links', 'data', 'meta'}
        for member in extra_members:
            assert getattr(obj, member) == valid_data[member]
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data with extra members {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # 'links' with extra fields not allowed (assuming 'custom' is not allowed if extra='allow' only for fields defined)
        # However, RelationshipObject allows extra fields, so this may not raise an error unless validate_member_name fails
        # If extra fields are allowed in 'links' via 'extra="allow"', then no error unless extra members have invalid names
        # So, test with invalid extra member names
        (
            {
                'links': {
                    'self': 'https://example.com/resource/7',
                    'invalid-link!': 'https://example.com/resource/7/invalid',
                }
            },
            ["Value error, Invalid link key 'invalid-link!' in RelationshipObject."],
        ),
        # Extra members with invalid names
        (
            {'links': {'self': 'https://example.com/resource/8'}, 'invalid_member@': 'Invalid value'},
            ["Invalid member name 'invalid_member@' according to JSON:API specification."],
        ),
    ],
)
def test_relationship_object_invalid_extra_members(invalid_data, expected_error_messages):
    """Test that extra members with invalid names raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        RelationshipObject(**invalid_data)

    actual_errors = exc_info.value.errors()
    expected_errors = (
        expected_error_messages if isinstance(expected_error_messages, list) else [expected_error_messages]
    )

    for expected_error in expected_errors:
        assert any(
            expected_error in error['msg'] for error in actual_errors
        ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_relationship_object_minimum_requirements():
    """Test that at least one of 'links', 'data', or 'meta' is present."""
    # Valid when 'links' is present
    data = {'links': {'self': 'https://example.com/resource/9'}}
    try:
        obj = RelationshipObject(**data)
        assert obj.links == data['links']
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'links' is present: {e}")

    # Valid when 'data' is present
    data = {'data': ResourceIdentifierObject(type='comments', id='15')}
    try:
        obj = RelationshipObject(**data)
        assert obj.data == data['data']
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'data' is present: {e}")

    # Valid when 'meta' is present
    data = {'meta': {'info': 'Some meta information'}}
    try:
        obj = RelationshipObject(**data)
        assert obj.meta == data['meta']
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'meta' is present: {e}")


def test_relationship_object_links_with_none_values():
    """Test that 'links' can have None values."""
    data = {'links': {'self': None, 'related': 'https://example.com/resource/10/related'}}
    try:
        obj = RelationshipObject(**data)
        assert obj.links == data['links']
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'links' have None values: {e}")


def test_relationship_object_data_as_none_with_links_present():
    """Test that 'data' can be None if 'links' or 'meta' are present."""
    data = {'links': {'self': 'https://example.com/resource/11'}, 'data': None}
    try:
        obj = RelationshipObject(**data)
        assert obj.links == data['links']
        assert obj.data is None
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'data' is None and 'links' are present: {e}")


def test_relationship_object_links_with_valid_and_invalid_values():
    """Test that 'links' can have a mix of valid and invalid values."""
    # Mixed valid and invalid 'links' values
    data = {'links': {'self': 'https://example.com/resource/12', 'related': 'invalid-uri'}}
    with pytest.raises(ValidationError) as exc_info:
        RelationshipObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Link 'related' must be a valid URI-reference."
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_relationship_object_data_with_invalid_resource_identifier():
    """Test that 'data' contains only ResourceIdentifierObject instances."""
    data = {'data': [ResourceIdentifierObject(type='tags', id='3'), 'invalid-resource-identifier']}
    with pytest.raises(ValidationError) as exc_info:
        RelationshipObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = 'Input should be a valid dictionary or instance of ResourceIdentifierObject'
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"
