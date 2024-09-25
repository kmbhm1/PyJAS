from pydantic import ValidationError
from pydantic_core import ErrorDetails
from pyjas.v1_1.jsonapi_builder import (
    ResourceIdentifierObject,
    RelationshipObject,
    ResourceObject,
    JSONAPIObject,
    Document,
)

import pytest


def clean_actual_errors(errors: list[ErrorDetails]) -> list[dict]:
    """Helper function to is_valid_uri up actual errors for comparison."""
    for e in errors:
        e.pop('ctx', None)  # Remove 'ctx' as it's not relevant for comparison
        e.pop('url', None)  # Remove 'url' as it's not relevant for comparison
    return errors


# Document class


# Test cases for the Document class
@pytest.mark.parametrize(
    'valid_data',
    [
        # Only 'data' with single ResourceObject
        {'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}, relationships={})},
        # Only 'data' with list of ResourceObject
        {
            'data': [
                ResourceObject(type='articles', id='1', attributes={'title': 'Test Article 1'}),
                ResourceObject(type='articles', id='2', attributes={'title': 'Test Article 2'}),
            ]
        },
        # Only 'data' with ResourceIdentifierObject
        {'data': ResourceIdentifierObject(type='articles', id='1')},
        # Only 'meta'
        {'meta': {'note': 'This is a meta object.'}},
        # Only 'jsonapi'
        {'jsonapi': JSONAPIObject(version='1.1', meta={'api_meta': 'value'})},
        # Only 'included' with list of ResourceObject
        {
            'data': ResourceObject(
                type='articles',
                id='1',
                attributes={'title': 'Test Article'},
                relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='9'))},
            ),
            'included': [ResourceObject(type='people', id='9', attributes={'name': 'John Doe'})],
        },
        # Combination of 'data', 'meta', and 'jsonapi'
        {
            'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}, relationships={}),
            'meta': {'note': 'Combined document.'},
            'jsonapi': JSONAPIObject(version='1.1'),
        },
        # Combination of 'data' and 'links'
        {
            'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}, relationships={}),
            'links': {'self': 'https://example.com/document'},
        },
        # Combination of 'data', 'included', and 'links'
        {
            'data': ResourceObject(
                type='articles',
                id='1',
                attributes={'title': 'Test Article'},
                relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='9'))},
            ),
            'included': [ResourceObject(type='people', id='9', attributes={'name': 'John Doe'})],
            'links': {'self': 'https://example.com/document'},
        },
        # 'included' with multiple ResourceObjects
        {
            'data': ResourceObject(
                type='articles',
                id='1',
                attributes={'title': 'Test Article'},
                relationships={
                    'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='9')),
                    'comments': RelationshipObject(
                        data=[
                            ResourceIdentifierObject(type='comments', id='5'),
                            ResourceIdentifierObject(type='comments', id='6'),
                        ]
                    ),
                },
            ),
            'included': [
                ResourceObject(type='people', id='9', attributes={'name': 'John Doe'}),
                ResourceObject(type='comments', id='5', attributes={'content': 'Great article!'}),
                ResourceObject(type='comments', id='6', attributes={'content': 'Thanks for sharing.'}),
            ],
        },
        # Document with extra members allowed by ConfigDict(extra='allow')
        {
            'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}, relationships={}),
            'custom_member': 'Custom Value',
            'another_member': {'key': 'value'},
        },
        # 'included' with unique resources
        {
            'data': ResourceObject(
                type='articles',
                id='1',
                attributes={'title': 'Test Article'},
                relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='9'))},
            ),
            'included': [
                ResourceObject(type='people', id='9', attributes={'name': 'John Doe'}),
            ],
        },
        # 'jsonapi' with default version
        {'jsonapi': JSONAPIObject()},
        # 'jsonapi' with allowed version and meta
        {'jsonapi': JSONAPIObject(version='1.0', meta={'info': 'Version 1.0 meta'})},
        # 'data' as None with 'meta' present
        {'data': None, 'meta': {'note': 'Data is None but meta is present.'}},
        # 'included' with empty list
        {
            'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}, relationships={}),
            'included': [],
        },
        # 'meta' with various data types
        {'meta': {'count': 10, 'active': True, 'items': ['item1', 'item2'], 'nested': {'key1': 'value1', 'key2': 2}}},
        # 'data' as list of ResourceIdentifierObject
        {
            'data': [
                ResourceIdentifierObject(type='articles', id='1'),
                ResourceIdentifierObject(type='articles', id='2'),
            ]
        },
        # 'data' as empty list
        {'data': []},
        # 'errors' as empty list
        {'errors': []},
        # 'jsonapi' with additional meta
        {'jsonapi': JSONAPIObject(version='1.1', meta={'documentation': 'https://example.com/docs'})},
        # 'included' with complex nested relationships
        {
            'data': ResourceObject(
                type='articles',
                id='1',
                attributes={'title': 'Complex Article'},
                relationships={
                    'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='9')),
                    'editor': RelationshipObject(data=ResourceIdentifierObject(type='people', id='10')),
                },
            ),
            'included': [
                ResourceObject(
                    type='people',
                    id='9',
                    attributes={'name': 'John Doe'},
                    relationships={
                        'manager': RelationshipObject(data=ResourceIdentifierObject(type='people', id='11'))
                    },
                ),
                ResourceObject(type='people', id='10', attributes={'name': 'Jane Smith'}),
            ],
        },
    ],
)
def test_document_valid(valid_data):
    """Test that valid Document instances are created successfully."""
    try:
        doc = Document(**{**valid_data})

        # Assert 'data' field
        if 'data' in valid_data:
            assert doc.data == valid_data['data']
        else:
            assert doc.data is None

        # Assert 'errors' field
        if 'errors' in valid_data:
            assert doc.errors == valid_data['errors']
        else:
            assert doc.errors is None

        # Assert 'meta' field
        if 'meta' in valid_data:
            assert doc.meta == valid_data['meta']
        else:
            assert doc.meta is None

        # Assert 'jsonapi' field
        if 'jsonapi' in valid_data:
            assert doc.jsonapi == valid_data['jsonapi']
        else:
            assert doc.jsonapi is None

        # Assert 'links' field
        if 'links' in valid_data:
            assert doc.links == valid_data['links']
        else:
            assert doc.links is None

        # Assert 'included' field
        if 'included' in valid_data:
            assert doc.included == valid_data['included']
        else:
            assert doc.included is None

        # Assert extra members
        extra_members = set(valid_data.keys()) - {'data', 'errors', 'meta', 'jsonapi', 'links', 'included'}
        for member in extra_members:
            assert getattr(doc, member) == valid_data[member]

    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # 0. Missing 'data' but including 'included'
        (
            {'included': [ResourceObject(type='people', id='9', attributes={'name': 'John Doe'})]},
            ["Value error, A document MUST contain at least one of 'data', 'errors', 'meta', or 'jsonapi'."],
        ),
        # 1. 'included' with duplicate resources
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='1',
                    attributes={'title': 'Duplicate Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='9'))},
                ),
                'included': [
                    ResourceObject(type='people', id='9', attributes={'name': 'John Doe'}),
                    ResourceObject(type='people', id='9', attributes={'name': 'John Doe Duplicate'}),
                ],
            },
            ["Duplicate resource in 'included': type='people', id='9' or lid='None'."],
        ),
        # 2. 'included' with resources not linked from 'data'
        (
            {
                'data': ResourceObject(
                    type='articles', id='1', attributes={'title': 'Unlinked Article'}, relationships={}
                ),
                'included': [ResourceObject(type='people', id='10', attributes={'name': 'Jane Smith'})],
            },
            ["Included resources are not reachable from primary data: {('people', '10')}"],
        ),
        # 3. Document with 'links' containing invalid keys
        (
            {
                'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}),
                'links': {'invalid_link': 'https://example.com/document'},
            },
            ["Value error, Invalid link key 'invalid_link' in Document."],
        ),
        # 4. Document with 'links' containing invalid link values
        (
            {
                'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}),
                'links': {
                    'self': 12345  # Invalid type
                },
            },
            ['Input should be a valid string'],
        ),
        # 5. Document with 'links' containing invalid URI string
        (
            {
                'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}),
                'links': {'self': 'invalid-uri'},
            },
            ["Value error, Link 'self' must be a valid URI-reference."],
        ),
        # 6. 'included' with 'included' resources not linked from 'data'
        (
            {
                'data': ResourceObject(type='articles', id='1', attributes={'title': 'Main Article'}, relationships={}),
                'included': [ResourceObject(type='people', id='11', attributes={'name': 'Unlinked Person'})],
            },
            ["Included resources are not reachable from primary data: {('people', '11')}"],
        ),
        # 7. 'included' with invalid ResourceObject
        (
            {
                'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}, relationships={}),
                'included': ['invalid-included-resource'],
            },
            ['Input should be a valid dictionary or instance of ResourceObject'],
        ),
        # 8. 'included' not a list
        (
            {
                'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}),
                'included': 'not-a-list',
            },
            ['Input should be a valid list'],
        ),
        # 9. Extra members with invalid names
        (
            {
                'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}),
                'invalid-member!': 'Invalid Value',
            },
            ["Invalid member name 'invalid-member!' according to JSON:API specification."],
        ),
        # 10. Document missing 'jsonapi' but including extra members that require validation
        (
            {
                'data': ResourceObject(type='articles', id='1', attributes={'title': 'Test Article'}),
                'another_invalid!': 'Invalid',
            },
            ["Invalid member name 'another_invalid!' according to JSON:API specification."],
        ),
        # 11. 'data' as list containing invalid types
        (
            {
                'data': [
                    ResourceObject(type='articles', id='1', attributes={'title': 'Valid Article'}),
                    'invalid-data-item',
                ]
            },
            ['Input should be a valid dictionary or instance of ResourceObject'],
        ),
        # 12. 'data' as invalid type (not ResourceObject or ResourceIdentifierObject or list)
        (
            {'data': 'invalid-data-type'},
            ['Input should be a valid dictionary or instance of ResourceObject'],
        ),
        # 13. 'included' with duplicate resources by 'lid'
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='1',
                    attributes={'title': 'Duplicate LID Article'},
                    relationships={
                        'author': RelationshipObject(data=ResourceIdentifierObject(type='people', lid='local-1'))
                    },
                ),
                'included': [
                    ResourceObject(type='people', lid='local-1', attributes={'name': 'John Doe'}),
                    ResourceObject(type='people', lid='local-1', attributes={'name': 'Jane Smith'}),
                ],
            },
            ["Duplicate resource in 'included': type='people', id='None' or lid='local-1'."],
        ),
        # 14. 'included' with resources not unique by type and id/lid
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='1',
                    attributes={'title': 'Unique Included Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='9'))},
                ),
                'included': [
                    ResourceObject(type='people', id='9', attributes={'name': 'John Doe'}),
                    ResourceObject(type='people', id='9', attributes={'name': 'John Doe Duplicate'}),
                ],
            },
            ["Duplicate resource in 'included': type='people', id='9' or lid='None'."],
        ),
    ],
)
def test_document_invalid(invalid_data, expected_error_messages):
    """Test that invalid Document instances raise ValidationError with correct messages."""
    with pytest.raises(ValidationError) as exc_info:
        Document(**invalid_data)

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
        # 'data' as single ResourceObject
        {
            'data': ResourceObject(
                type='articles', id='2', attributes={'title': 'Another Test Article'}, relationships={}
            )
        },
        # 'data' as list of ResourceIdentifierObject
        {
            'data': [
                ResourceIdentifierObject(type='articles', id='3'),
                ResourceIdentifierObject(type='articles', id='4'),
            ]
        },
        # 'jsonapi' with meta
        {'jsonapi': JSONAPIObject(version='1.1', meta={'api_meta': 'value'})},
        # 'included' with multiple ResourceObjects correctly linked
        {
            'data': ResourceObject(
                type='articles',
                id='5',
                attributes={'title': 'Linked Article'},
                relationships={
                    'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='12')),
                    'comments': RelationshipObject(
                        data=[
                            ResourceIdentifierObject(type='comments', id='7'),
                            ResourceIdentifierObject(type='comments', id='8'),
                        ]
                    ),
                },
            ),
            'included': [
                ResourceObject(type='people', id='12', attributes={'name': 'Alice Wonderland'}),
                ResourceObject(type='comments', id='7', attributes={'content': 'Great read!'}),
                ResourceObject(type='comments', id='8', attributes={'content': 'Very informative.'}),
            ],
        },
        # 'meta' with nested structures
        {
            'meta': {
                'analytics': {'page_views': 1500, 'unique_visitors': 1200},
                'preferences': {'theme': 'dark', 'notifications': True},
            }
        },
        # Combination of 'data', 'included', 'links', and 'jsonapi'
        {
            'data': ResourceObject(
                type='articles',
                id='6',
                attributes={'title': 'Comprehensive Test Article'},
                relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='13'))},
            ),
            'included': [ResourceObject(type='people', id='13', attributes={'name': 'Bob Builder'})],
            'links': {'self': 'https://example.com/document/6', 'related': 'https://example.com/related/6'},
            'jsonapi': JSONAPIObject(version='1.0', meta={'documentation': 'https://example.com/docs'}),
        },
        # 'data' as list with mixed ResourceObject and ResourceIdentifierObject
        # {
        #     'data': [
        #         ResourceObject(type='articles', id='7', attributes={'title': 'Mixed Data Article'}),
        #         ResourceIdentifierObject(type='people', id='14'),
        #     ]
        # },
        # 'included' with linked resources via 'lid'
        {
            'data': ResourceObject(
                type='articles',
                id='8',
                attributes={'title': 'LID Linked Article'},
                relationships={
                    'editor': RelationshipObject(data=ResourceIdentifierObject(type='people', lid='local-14'))
                },
            ),
            'included': [ResourceObject(type='people', lid='local-14', attributes={'name': 'Charlie Chocolate'})],
        },
        # 'included' with nested relationships
        {
            'data': ResourceObject(
                type='projects',
                id='9',
                attributes={'name': 'Project X'},
                relationships={'leader': RelationshipObject(data=ResourceIdentifierObject(type='people', id='15'))},
            ),
            'included': [
                ResourceObject(
                    type='people',
                    id='15',
                    attributes={'name': 'Dana Scully'},
                    relationships={
                        'department': RelationshipObject(data=ResourceIdentifierObject(type='departments', id='3'))
                    },
                ),
            ],
        },
        # 'included' with unique lid
        {
            'data': ResourceObject(
                type='articles',
                id='10',
                attributes={'title': 'LID Unique Article'},
                relationships={
                    'author': RelationshipObject(data=ResourceIdentifierObject(type='people', lid='local-15'))
                },
            ),
            'included': [ResourceObject(type='people', lid='local-15', attributes={'name': 'Eve Online'})],
        },
    ],
)
def test_document_additional_valid_cases(valid_data):
    """Test additional valid Document instances."""
    try:
        doc = Document(**valid_data)

        # Assert 'data' field
        if 'data' in valid_data:
            assert doc.data == valid_data['data']
        else:
            assert doc.data is None

        # Assert 'errors' field
        if 'errors' in valid_data:
            assert doc.errors == valid_data['errors']
        else:
            assert doc.errors is None

        # Assert 'meta' field
        if 'meta' in valid_data:
            assert doc.meta == valid_data['meta']
        else:
            assert doc.meta is None

        # Assert 'jsonapi' field
        if 'jsonapi' in valid_data:
            assert doc.jsonapi == valid_data['jsonapi']
        else:
            assert doc.jsonapi is None

        # Assert 'links' field
        if 'links' in valid_data:
            assert doc.links == valid_data['links']
        else:
            assert doc.links is None

        # Assert 'included' field
        if 'included' in valid_data:
            assert doc.included == valid_data['included']
        else:
            assert doc.included is None

        # Assert extra members
        extra_members = set(valid_data.keys()) - {'data', 'errors', 'meta', 'jsonapi', 'links', 'included'}
        for member in extra_members:
            assert getattr(doc, member) == valid_data[member]

    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for additional valid data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # Missing all of 'data', 'errors', 'meta', 'jsonapi'
        ({}, ["A document MUST contain at least one of 'data', 'errors', 'meta', or 'jsonapi'."]),
        # Missing 'data' but including 'included'
        (
            {'included': [ResourceObject(type='people', id='9', attributes={'name': 'John Doe'})]},
            ["A document MUST contain at least one of 'data', 'errors', 'meta', or 'jsonapi'."],
        ),
        # 'included' with duplicate resources by 'id'
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='2',
                    attributes={'title': 'Duplicate ID Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='16'))},
                ),
                'included': [
                    ResourceObject(type='people', id='16', attributes={'name': 'Frank Ocean'}),
                    ResourceObject(type='people', id='16', attributes={'name': 'Frank Ocean Duplicate'}),
                ],
            },
            ["Duplicate resource in 'included': type='people', id='16' or lid='None'."],
        ),
        # 'included' with duplicate resources by 'lid'
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='3',
                    attributes={'title': 'Duplicate LID Article'},
                    relationships={
                        'editor': RelationshipObject(data=ResourceIdentifierObject(type='people', lid='local-17'))
                    },
                ),
                'included': [
                    ResourceObject(type='people', lid='local-17', attributes={'name': 'Grace Hopper'}),
                    ResourceObject(type='people', lid='local-17', attributes={'name': 'Grace Hopper Duplicate'}),
                ],
            },
            ["Duplicate resource in 'included': type='people', id='None' or lid='local-17'."],
        ),
        # 'included' with resources not linked from 'data'
        (
            {
                'data': ResourceObject(
                    type='articles', id='4', attributes={'title': 'Unlinked Included Article'}, relationships={}
                ),
                'included': [ResourceObject(type='people', id='18', attributes={'name': 'Hank Pym'})],
            },
            ["Included resources are not reachable from primary data: {('people', '18')}"],
        ),
        # 'included' not a list
        (
            {
                'data': ResourceObject(
                    type='articles', id='5', attributes={'title': 'Invalid Included Article'}, relationships={}
                ),
                'included': 'not-a-list',
            },
            ['Input should be a valid list'],
        ),
        # 'included' with invalid ResourceObject
        (
            {
                'data': ResourceObject(
                    type='articles', id='6', attributes={'title': 'Invalid Included Article'}, relationships={}
                ),
                'included': ['invalid-included-resource'],
            },
            ['Input should be a valid dictionary'],
        ),
        # Document with 'links' containing invalid keys
        (
            {
                'data': ResourceObject(
                    type='articles', id='8', attributes={'title': 'Invalid Links Article'}, relationships={}
                ),
                'links': {'invalid_link': 'https://example.com/document/8'},
            },
            ["Invalid link key 'invalid_link' in Document."],
        ),
        # Document with 'links' containing invalid link values
        (
            {
                'data': ResourceObject(
                    type='articles', id='9', attributes={'title': 'Invalid Link Values Article'}, relationships={}
                ),
                'links': {
                    'self': 12345  # Invalid type
                },
            },
            ['Input should be a valid string'],
        ),
        # Document with 'links' containing invalid URI string
        (
            {
                'data': ResourceObject(
                    type='articles', id='10', attributes={'title': 'Invalid URI Links Article'}, relationships={}
                ),
                'links': {'self': 'invalid-uri'},
            },
            ["Link 'self' must be a valid URI-reference."],
        ),
        # Document with extra members having invalid names
        (
            {
                'data': ResourceObject(
                    type='articles', id='12', attributes={'title': 'Extra Members Article'}, relationships={}
                ),
                'invalid_member!': 'Invalid Value',
            },
            ["Invalid member name 'invalid_member!' according to JSON:API specification."],
        ),
        # Document with 'meta' as non-dictionary
        ({'meta': 'not-a-dict'}, ['Input should be a valid dictionary']),
        # Document with 'errors' as non-list
        ({'errors': 'not-a-list'}, ['Input should be a valid list']),
        # Document with 'data' as invalid type
        (
            {'data': 'invalid-data-type'},
            ['Input should be a valid dictionary or instance of ResourceObject'],
        ),
        # Document with 'included' containing invalid types
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='13',
                    attributes={'title': 'Included Invalid Types Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='19'))},
                ),
                'included': [
                    ResourceObject(type='people', id='19', attributes={'name': 'Ivy League'}),
                    'invalid-included-resource',
                ],
            },
            ['Input should be a valid dictionary or instance of ResourceObject'],
        ),
        # 'included' with resources not unique by type and id/lid
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='14',
                    attributes={'title': 'Unique Included Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='20'))},
                ),
                'included': [
                    ResourceObject(type='people', id='20', attributes={'name': 'Jack Sparrow'}),
                    ResourceObject(type='people', id='20', attributes={'name': 'Jack Sparrow Duplicate'}),
                ],
            },
            ["Duplicate resource in 'included': type='people', id='20' or lid='None'."],
        ),
    ],
)
def test_document_invalid_2(invalid_data, expected_error_messages):
    """Test that invalid Document instances raise ValidationError with correct messages."""
    with pytest.raises(ValidationError) as exc_info:
        Document(**invalid_data)

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
        # 'data' as single ResourceObject with nested relationships
        {
            'data': ResourceObject(
                type='articles',
                id='15',
                attributes={'title': 'Nested Relationships Article'},
                relationships={
                    'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='21')),
                    'editor': RelationshipObject(data=ResourceIdentifierObject(type='people', id='22')),
                },
            ),
            'included': [
                ResourceObject(type='people', id='21', attributes={'name': 'Karen Page'}),
                ResourceObject(type='people', id='22', attributes={'name': 'Luke Cage'}),
            ],
        },
        # Document with all possible fields
        {
            'data': ResourceObject(
                type='projects',
                id='17',
                attributes={'name': 'Project Omega'},
                relationships={'manager': RelationshipObject(data=ResourceIdentifierObject(type='people', id='24'))},
            ),
            'errors': None,  # 'errors' can be None
            'meta': {'created_at': '2024-04-01', 'updated_at': '2024-04-15'},
            'jsonapi': JSONAPIObject(version='1.1', meta={'documentation': 'https://example.com/docs'}),
            'links': {'self': 'https://example.com/projects/17'},
            'included': [ResourceObject(type='people', id='24', attributes={'name': 'Ned Stark'})],
        },
        # Document with 'data' as None and 'meta' present
        {'data': None, 'meta': {'info': 'No primary data, but meta is present.'}},
        # Document with 'data' as empty list
        {'data': []},
        # Document with 'errors' as empty list
        {'errors': []},
        # Document with 'included' as empty list and 'data' present
        {
            'data': ResourceObject(type='articles', id='18', attributes={'title': 'Included Empty Article'}),
            'included': [],
        },
    ],
)
def test_document_additional_valid_cases_2(valid_data):
    """Test additional valid Document instances with various field combinations."""
    try:
        doc = Document(**valid_data)

        # Assert 'data' field
        if 'data' in valid_data:
            assert doc.data == valid_data['data']
        else:
            assert doc.data is None

        # Assert 'errors' field
        if 'errors' in valid_data:
            assert doc.errors == valid_data['errors']
        else:
            assert doc.errors is None

        # Assert 'meta' field
        if 'meta' in valid_data:
            assert doc.meta == valid_data['meta']
        else:
            assert doc.meta is None

        # Assert 'jsonapi' field
        if 'jsonapi' in valid_data:
            assert doc.jsonapi == valid_data['jsonapi']
        else:
            assert doc.jsonapi is None

        # Assert 'links' field
        if 'links' in valid_data:
            assert doc.links == valid_data['links']
        else:
            assert doc.links is None

        # Assert 'included' field
        if 'included' in valid_data:
            assert doc.included == valid_data['included']
        else:
            assert doc.included is None

        # Assert extra members
        extra_members = set(valid_data.keys()) - {'data', 'errors', 'meta', 'jsonapi', 'links', 'included'}
        for member in extra_members:
            assert getattr(doc, member) == valid_data[member]

    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for additional valid data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # 'data' as list containing invalid types
        (
            {
                'data': [
                    ResourceObject(type='articles', id='19', attributes={'title': 'Valid Article'}),
                    'invalid-data-item',
                ]
            },
            ['Input should be a valid dictionary or instance of ResourceObject'],
        ),
        # 'included' with duplicate resources by 'type' and 'id'
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='20',
                    attributes={'title': 'Duplicate Included Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='25'))},
                ),
                'included': [
                    ResourceObject(type='people', id='25', attributes={'name': 'Peter Parker'}),
                    ResourceObject(type='people', id='25', attributes={'name': 'Peter Parker Duplicate'}),
                ],
            },
            ["Duplicate resource in 'included': type='people', id='25' or lid='None'."],
        ),
        # 'included' with ResourceObject missing 'id' and 'lid'
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='21',
                    attributes={'title': 'Included Missing ID Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='26'))},
                ),
                'included': [ResourceObject(type='people', id='1', attributes={'name': 'Quentin Tarantino'})],
            },
            ['Value error, Included resources are not reachable from primary data'],
        ),
        # Document with 'meta' as non-dictionary
        ({'meta': 'invalid-meta'}, ['Input should be a valid dictionary']),
        # Document with 'errors' as non-list
        ({'errors': 'invalid-errors'}, ['Input should be a valid list']),
        # Document with 'included' containing non-ResourceObject items
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='25',
                    attributes={'title': 'Included Non-ResourceObject Article'},
                    relationships={},
                ),
                'included': [
                    ResourceObject(type='people', id='27', attributes={'name': 'Rachel Green'}),
                    'invalid-included-resource',
                ],
            },
            ['Input should be a valid dictionary or instance of ResourceObject'],
        ),
        # Document with 'included' not linked to 'data'
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='27',
                    attributes={'title': 'Unlinked Included Resources Article'},
                    relationships={},
                ),
                'included': [ResourceObject(type='people', id='29', attributes={'name': 'Tony Stark'})],
            },
            ["Included resources are not reachable from primary data: {('people', '29')}"],
        ),
        # Document with 'links' containing unsupported keys
        (
            {
                'data': ResourceObject(
                    type='articles', id='28', attributes={'title': 'Unsupported Links Article'}, relationships={}
                ),
                'links': {
                    'pagination': 'https://example.com/document/pagination'  # Unsupported key
                },
            },
            ["Value error, Invalid link key 'pagination' in Document."],
        ),
        # Document with 'included' containing resources without 'id' and 'lid'
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='29',
                    attributes={'title': 'Included Resources Missing ID Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='30'))},
                ),
                'included': [ResourceObject(type='people', id='67', attributes={'name': 'Uma Thurman'})],
            },
            ['Value error, Included resources are not reachable from primary data'],
        ),
    ],
)
def test_document_invalid_cases(invalid_data, expected_error_messages):
    """Test that invalid Document instances raise ValidationError with correct messages."""
    with pytest.raises(ValidationError) as exc_info:
        Document(**invalid_data)

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
        # Document with 'data' and extra members
        {
            'data': ResourceObject(
                type='articles', id='30', attributes={'title': 'Extra Members Article'}, relationships={}
            ),
            'extra_field1': 'Extra Value 1',
            'extra_field2': {'key': 'Extra Value 2'},
        },
        # Document with 'jsonapi' and extra members
        {'jsonapi': JSONAPIObject(version='1.1', meta={'doc_meta': 'some value'}), 'custom_member': 'Custom Value'},
        # Document with all fields and multiple extra members
        {
            'data': ResourceObject(
                type='articles', id='31', attributes={'title': 'Full Featured Article'}, relationships={}
            ),
            'meta': {'note': 'Full document.'},
            'jsonapi': JSONAPIObject(version='1.0'),
            'links': {'self': 'https://example.com/document/31'},
            'included': [],
            'extra1': 'Extra1',
            'extra2': 'Extra2',
        },
    ],
)
def test_document_with_extra_members(valid_data):
    """Test that Document accepts extra members with valid names."""
    try:
        doc = Document(**valid_data)

        # Assert 'data' field
        if 'data' in valid_data:
            assert doc.data == valid_data['data']
        else:
            assert doc.data is None

        # Assert 'errors' field
        if 'errors' in valid_data:
            assert doc.errors == valid_data['errors']
        else:
            assert doc.errors is None

        # Assert 'meta' field
        if 'meta' in valid_data:
            assert doc.meta == valid_data['meta']
        else:
            assert doc.meta is None

        # Assert 'jsonapi' field
        if 'jsonapi' in valid_data:
            assert doc.jsonapi == valid_data['jsonapi']
        else:
            assert doc.jsonapi is None

        # Assert 'links' field
        if 'links' in valid_data:
            assert doc.links == valid_data['links']
        else:
            assert doc.links is None

        # Assert 'included' field
        if 'included' in valid_data:
            assert doc.included == valid_data['included']
        else:
            assert doc.included is None

        # Assert extra members
        extra_members = set(valid_data.keys()) - {'data', 'errors', 'meta', 'jsonapi', 'links', 'included'}
        for member in extra_members:
            assert getattr(doc, member) == valid_data[member]

    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data with extra members {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # Document with extra members having invalid names
        (
            {
                'data': ResourceObject(
                    type='articles', id='32', attributes={'title': 'Invalid Extra Members Article'}, relationships={}
                ),
                'invalid_member!': 'Invalid Value',
            },
            ["Invalid member name 'invalid_member!' according to JSON:API specification."],
        ),
        # Document with 'data' and 'included' but 'included' not linked
        (
            {
                'data': ResourceObject(
                    type='articles', id='33', attributes={'title': 'Unlinked Included Article'}, relationships={}
                ),
                'included': [ResourceObject(type='people', id='34', attributes={'name': 'Victor Stone'})],
                'extra_invalid_field': 'Invalid',
            },
            ['Value error, Included resources are not reachable from primary data:'],
        ),
        # Document with 'included' containing invalid member names
        (
            {
                'data': ResourceObject(
                    type='articles',
                    id='35',
                    attributes={'title': 'Included Invalid Member Names Article'},
                    relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='35'))},
                ),
                'included': [
                    ResourceObject(
                        type='people',
                        id='35',
                        attributes={'name': 'Walter White'},
                        relationships={
                            'invalid_relationship!': RelationshipObject(
                                data=ResourceIdentifierObject(type='departments', id='4')
                            )
                        },
                    )
                ],
                'invalid_member@': 'Invalid',
            },
            [
                "Value error, Invalid member name 'invalid_member@'",
            ],
        ),
    ],
)
def test_document_invalid_extra_members(invalid_data, expected_error_messages):
    """Test that Document rejects extra members with invalid names."""
    with pytest.raises(ValidationError) as exc_info:
        Document(**invalid_data)

    actual_errors = exc_info.value.errors()
    expected_errors = (
        expected_error_messages if isinstance(expected_error_messages, list) else [expected_error_messages]
    )

    for expected_error in expected_errors:
        # Check if any of the actual errors contain the expected error message
        assert any(
            expected_error in error['msg'] for error in actual_errors
        ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_document_validate_document_relationships_and_included():
    """Test that all included resources are reachable from primary data."""
    # Create a data ResourceObject with relationships pointing to included resources
    data = ResourceObject(
        type='articles',
        id='38',
        attributes={'title': 'Reachable Included Article'},
        relationships={
            'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='39')),
            'comments': RelationshipObject(
                data=[
                    ResourceIdentifierObject(type='comments', id='40'),
                    ResourceIdentifierObject(type='comments', id='41'),
                ]
            ),
        },
    )

    # Create included ResourceObjects that are linked
    included = [
        ResourceObject(type='people', id='39', attributes={'name': 'Yvonne Strahovski'}),
        ResourceObject(type='comments', id='40', attributes={'content': 'Great article!'}),
        ResourceObject(type='comments', id='41', attributes={'content': 'Very informative.'}),
    ]

    # Valid document
    valid_document = {'data': data, 'included': included}

    try:
        doc = Document(**valid_document)
        assert doc.data == data
        assert doc.included == included
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for reachable included resources: {e}')

    # Invalid document: included resource not linked from data
    invalid_document = {
        'data': data,
        'included': included + [ResourceObject(type='people', id='42', attributes={'name': 'Zachary Levi'})],
    }

    with pytest.raises(ValidationError) as exc_info:
        Document(**invalid_document)

    actual_errors = exc_info.value.errors()
    expected_error = "Included resources are not reachable from primary data: {('people', '42')}"
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_document_validate_document_data_as_none_with_meta():
    """Test that 'data' can be None if 'meta' or 'jsonapi' is present."""
    valid_data = {'data': None, 'meta': {'info': 'Data is None, but meta is present.'}}

    try:
        doc = Document(**valid_data)
        assert doc.data is None
        assert doc.meta == valid_data['meta']
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'data' is None with 'meta': {e}")


def test_document_validate_document_data_as_none_without_meta():
    """Test that 'data' can be None if 'jsonapi' is present."""
    valid_data = {
        'data': None,
        'jsonapi': JSONAPIObject(version='1.1', meta={'documentation': 'https://example.com/docs'}),
    }

    try:
        doc = Document(**valid_data)
        assert doc.data is None
        assert doc.jsonapi == valid_data['jsonapi']
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'data' is None with 'jsonapi': {e}")


def test_document_validate_document_data_as_none_without_meta_or_jsonapi():
    """Test that 'data' can be None only if 'meta' or 'jsonapi' is present."""
    valid_data = {
        'data': None,
        'meta': {'info': 'Data is None, but meta is present.'},
        'jsonapi': JSONAPIObject(version='1.1'),
    }

    try:
        doc = Document(**valid_data)
        assert doc.data is None
        assert doc.meta == valid_data['meta']
        assert doc.jsonapi == valid_data['jsonapi']
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly when 'data' is None with 'meta' and 'jsonapi': {e}")


def test_document_validate_document_included_with_lid():
    """Test that 'included' resources with 'lid' are correctly linked."""
    data = ResourceObject(
        type='articles',
        id='43',
        attributes={'title': 'Included with LID Article'},
        relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', lid='local-44'))},
    )

    included = [ResourceObject(type='people', lid='local-44', attributes={'name': "Brian O'Conner"})]

    valid_document = {'data': data, 'included': included}

    try:
        doc = Document(**valid_document)
        assert doc.data == data
        assert doc.included == included
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly for included resource with 'lid': {e}")


def test_document_validate_document_included_resources_reachable():
    """Test that all included resources are reachable from primary data."""
    data = ResourceObject(
        type='projects',
        id='44',
        attributes={'name': 'Project Reachable'},
        relationships={
            'leader': RelationshipObject(data=ResourceIdentifierObject(type='people', id='45')),
            'team': RelationshipObject(
                data=[
                    ResourceIdentifierObject(type='people', id='46'),
                    ResourceIdentifierObject(type='people', id='47'),
                ]
            ),
        },
    )

    included = [
        ResourceObject(type='people', id='45', attributes={'name': 'Charlie Brown'}),
        ResourceObject(type='people', id='46', attributes={'name': 'Lucy van Pelt'}),
        ResourceObject(type='people', id='47', attributes={'name': 'Linus van Pelt'}),
    ]

    valid_document = {'data': data, 'included': included}

    try:
        doc = Document(**valid_document)
        assert doc.data == data
        assert doc.included == included
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for reachable included resources: {e}')

    # Now, add an unreachable included resource
    invalid_document = {
        'data': data,
        'included': included + [ResourceObject(type='people', id='48', attributes={'name': 'Sally Brown'})],
    }

    with pytest.raises(ValidationError) as exc_info:
        Document(**invalid_document)

    actual_errors = exc_info.value.errors()
    expected_error = "Included resources are not reachable from primary data: {('people', '48')}"
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"
