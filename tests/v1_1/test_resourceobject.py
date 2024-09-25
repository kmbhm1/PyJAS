from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails
from pyjas.v1_1.jsonapi_builder import (
    ResourceIdentifierObject,
    RelationshipObject,
    ResourceObject,
)

import pytest


def clean_actual_errors(errors: list[ErrorDetails]) -> list[dict]:
    """Helper function to is_valid_uri up actual errors for comparison."""
    for e in errors:
        e.pop('ctx', None)  # Remove 'ctx' as it's not relevant for comparison
        e.pop('url', None)  # Remove 'url' as it's not relevant for comparison
    return errors


# ResourceObject tests


@pytest.mark.parametrize(
    'valid_data',
    [
        # 'type' and 'id'
        {'type': 'users', 'id': 'user123'},
        # 'type' and 'lid'
        {'type': 'comments', 'lid': 'local-456'},
        # 'type', 'id', and 'lid'
        {'type': 'posts', 'id': 'post789', 'lid': 'local-post789'},
        # 'type' and 'attributes'
        {
            'type': 'categories',
            'id': 'foo',
            'attributes': {'name': 'Technology', 'description': 'All tech-related articles.'},
        },
        # 'type' and 'relationships'
        {
            'type': 'articles',
            'id': '1',
            'relationships': {
                'author': RelationshipObject(
                    links={'self': 'https://example.com/articles/1/relationships/author'},
                    data=ResourceIdentifierObject(type='people', id='9'),
                )
            },
        },
        # 'type' and 'links'
        # {
        #     'type': 'articles',
        #     'id': '6789',
        #     'links': {
        #         'self': 'https://example.com/articles/1',
        #         'related': LinkObject(href='https://example.com/articles/1/related', rel='related'),
        #     },
        # },
        # 'type' and 'meta'
        {'type': 'articles', 'id': '1', 'meta': {'last_updated': '2024-01-01', 'revision': 2}},
        # All optional fields present
        {
            'type': 'articles',
            'id': '1',
            'lid': 'local-1',
            'attributes': {'title': 'Understanding Pydantic', 'content': 'Pydantic is a data validation library...'},
            'relationships': {
                'author': RelationshipObject(
                    links={'self': 'https://example.com/articles/1/relationships/author'},
                    data=ResourceIdentifierObject(type='people', id='9'),
                )
            },
            'links': {'self': 'https://example.com/articles/1', 'related': 'https://example.com/articles/1/related'},
            'meta': {'revision': 3},
        },
        # Attributes without reserved keys and without foreign keys
        {'type': 'tags', 'id': '1', 'attributes': {'name': 'python', 'description': 'All about Python programming.'}},
        # Relationships without reserved keys and valid ResourceIdentifierObjects
        {
            'type': 'articles',
            'id': '1',
            'relationships': {
                'comments': RelationshipObject(
                    data=[
                        ResourceIdentifierObject(type='comments', id='5'),
                        ResourceIdentifierObject(type='comments', lid='local-123'),
                    ]
                )
            },
        },
        # Links with valid keys and URIs
        {
            'type': 'articles',
            'id': '1',
            'links': {
                'self': 'https://example.com/articles/2',
                'related': 'https://example.com/articles/2/related',
                'describedby': 'https://example.com/schema/articles',
            },
        },
        # Attributes with nested data but no foreign keys
        {
            'type': 'profiles',
            'id': '1',
            'attributes': {
                'bio': 'Software developer and writer.',
                'social': {'twitter': '@devwriter', 'github': 'devwriter'},
            },
        },
        # 'lid' uniqueness is assumed to be handled outside of this model; including unique 'lid'
        {
            'type': 'users',
            'lid': 'unique-lid-001',
            'attributes': {'username': 'johndoe', 'email': 'johndoe@example.com'},
        },
        # Complex attributes and relationships
        {
            'type': 'projects',
            'id': 'proj123',
            'attributes': {
                'name': 'AI Research',
                'budget': 100000,
                'details': {'duration': '12 months', 'team_size': 10},
            },
            'relationships': {
                'lead': RelationshipObject(data=ResourceIdentifierObject(type='people', id='7')),
                'members': RelationshipObject(
                    data=[
                        ResourceIdentifierObject(type='people', id='8'),
                        ResourceIdentifierObject(type='people', id='9'),
                    ]
                ),
            },
            'links': {'self': 'https://example.com/projects/proj123'},
            'meta': {'priority': 'high'},
        },
    ],
)
def test_resource_object_valid(valid_data):
    """Test that valid ResourceObject instances are created successfully."""
    try:
        obj = ResourceObject(**valid_data)
        # Assert required field 'type'
        assert obj.type_ == valid_data['type']

        # Assert 'id' and 'lid' if present
        if 'id' in valid_data:
            assert obj.id_ == valid_data['id']
        else:
            assert obj.id_ is None

        if 'lid' in valid_data:
            assert obj.lid == valid_data['lid']
        else:
            assert obj.lid is None

        # Assert 'attributes' if present
        if 'attributes' in valid_data:
            assert obj.attributes == valid_data['attributes']
        else:
            assert obj.attributes is None

        # Assert 'relationships' if present
        if 'relationships' in valid_data:
            assert obj.relationships == valid_data['relationships']
        else:
            assert obj.relationships is None

        # Assert 'links' if present
        if 'links' in valid_data:
            assert obj.links == valid_data['links']
        else:
            assert obj.links is None

        # Assert 'meta' if present
        if 'meta' in valid_data:
            assert obj.meta == valid_data['meta']
        else:
            assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_error_messages',
    [
        # Missing required 'type' field
        ({'id': 'user123'}, ['Field required']),
        # Missing both 'id' and 'lid'
        ({'type': 'users'}, ["ResourceObject must have either 'id' or 'lid'."]),
        # 'type' not being a string
        ({'type': 123, 'id': 'user123'}, ['Input should be a valid string']),
        # 'id' not being a string
        ({'type': 'users', 'id': 456}, ['Input should be a valid string']),
        # 'lid' not being a string
        ({'type': 'users', 'lid': 789}, ['Input should be a valid string']),
        # Attributes containing reserved keys ('type')
        (
            {'type': 'articles', 'id': '1', 'attributes': {'type': 'not-allowed'}},
            ["Attribute names {'type'} are reserved and cannot be used."],
        ),
        # Attributes containing reserved keys ('id')
        (
            {'type': 'articles', 'id': '1', 'attributes': {'id': 'not-allowed'}},
            ["Attribute names {'id'} are reserved and cannot be used."],
        ),
        # Attributes containing reserved keys ('lid')
        (
            {'type': 'articles', 'id': '1', 'attributes': {'lid': 'not-allowed'}},
            ["Attribute names {'lid'} are reserved and cannot be used."],
        ),
        # Attributes containing foreign keys
        (
            {'type': 'posts', 'id': 'post1', 'attributes': {'title': 'First Post', 'author_id': 'author1'}},
            ["Attribute names {'author_id'} are reserved for relationships and should not appear in attributes."],
        ),
        # Relationships containing reserved keys ('type')
        (
            {
                'type': 'articles',
                'id': '1',
                'relationships': {
                    'type': RelationshipObject(
                        links={'self': 'https://example.com/articles/1/relationships/type'},
                        data=ResourceIdentifierObject(type='types', id='t1'),
                    )
                },
            },
            ["Relationship names {'type'} are reserved and cannot be used."],
        ),
        # Relationships containing reserved keys ('id')
        (
            {
                'type': 'articles',
                'id': '1',
                'relationships': {
                    'id': RelationshipObject(
                        links={'self': 'https://example.com/articles/1/relationships/id'},
                        data=ResourceIdentifierObject(type='ids', id='id1'),
                    )
                },
            },
            ["Relationship names {'id'} are reserved and cannot be used."],
        ),
        # Relationships containing reserved keys ('lid')
        (
            {
                'type': 'articles',
                'id': '1',
                'relationships': {
                    'lid': RelationshipObject(
                        links={'self': 'https://example.com/articles/1/relationships/lid'},
                        data=ResourceIdentifierObject(type='lids', lid='lid1'),
                    )
                },
            },
            ["Relationship names {'lid'} are reserved and cannot be used."],
        ),
        # 'links' containing invalid keys
        (
            {'type': 'articles', 'id': '1', 'links': {'invalid_link': 'https://example.com/articles/1/invalid'}},
            ["Value error, Invalid link key 'invalid_link' in ResourceObject."],
        ),
        # 'links' with invalid value type
        (
            {
                'type': 'articles',
                'id': '1',
                'links': {
                    'self': 12345  # Invalid type
                },
            },
            ['Input should be a valid dictionary or instance of LinkObject'],
        ),
        # 'links' with invalid URI string
        (
            {'type': 'articles', 'id': '1', 'links': {'self': 'invalid-uri'}},
            ["Link 'self' must be a valid URI-reference."],
        ),
        # Extra fields not allowed
        (
            {'type': 'articles', 'id': '1', 'extra_field': 'not allowed'},
            ['Extra inputs are not permitted'],
        ),
        # 'lid' not unique within the document (assuming uniqueness is handled externally; thus, model may not enforce)
        # If uniqueness is enforced within the model, then include such a test; otherwise, skip
        # For demonstration, assuming 'lid' uniqueness is not enforced in the model itself
        # So, no test case here
        # Conflicting keys between 'attributes' and 'relationships'
        (
            {
                'type': 'articles',
                'id': '1',
                'attributes': {'title': 'Sample Article'},
                'relationships': {'title': RelationshipObject(data=ResourceIdentifierObject(type='titles', id='t1'))},
            },
            ["Attribute and relationship names must not conflict. Conflicting names: {'title'}"],
        ),
        # 'attributes' as non-dictionary
        ({'type': 'articles', 'id': '1', 'attributes': 'not-a-dict'}, ['Input should be a valid dictionary']),
        # 'relationships' as non-dictionary
        ({'type': 'articles', 'id': '1', 'relationships': 'not-a-dict'}, ['Input should be a valid dictionary']),
        # 'links' as non-dictionary
        ({'type': 'articles', 'id': '1', 'links': 'not-a-dict'}, ['Input should be a valid dictionary']),
        # 'meta' as non-dictionary
        ({'type': 'articles', 'id': '1', 'meta': 'not-a-dict'}, ['Input should be a valid dictionary']),
        # 'attributes' containing multiple foreign keys
        (
            {
                'type': 'posts',
                'id': 'post1',
                'attributes': {'title': 'Post Title', 'author_id': 'author1', 'category_id': 'cat1'},
            },
            ['Value error, Attribute names'],
        ),
        # 'attributes' and 'relationships' sharing a reserved key
        (
            {
                'type': 'projects',
                'id': 'proj1',
                'attributes': {'name': 'Project Alpha'},
                'relationships': {'name': RelationshipObject(data=ResourceIdentifierObject(type='names', id='name1'))},
            },
            ['Value error, Attribute and relationship names must not conflict.'],
        ),
    ],
)
def test_resource_object_invalid(invalid_data, expected_error_messages):
    """Test that invalid ResourceObject instances raise ValidationError with correct messages."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**invalid_data)

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
        # Attributes without reserved keys and without foreign keys
        {'type': 'tags', 'id': '1', 'attributes': {'name': 'python', 'description': 'All about Python programming.'}},
        # Relationships without reserved keys and valid ResourceIdentifierObjects
        {
            'type': 'articles',
            'id': '2',
            'relationships': {
                'comments': RelationshipObject(
                    data=[
                        ResourceIdentifierObject(type='comments', id='5'),
                        ResourceIdentifierObject(type='comments', lid='local-123'),
                    ]
                )
            },
        },
        # Ensuring no foreign keys in attributes
        {'type': 'projects', 'id': '3', 'attributes': {'title': 'AI Research', 'budget': 100000}},
    ],
)
def test_resource_object_additional_valid_cases(valid_data):
    """Test additional valid ResourceObject instances."""
    try:
        obj = ResourceObject(**valid_data)
        assert obj.type_ == valid_data['type']

        if 'id' in valid_data:
            assert obj.id_ == valid_data['id']
        else:
            assert obj.id_ is None

        if 'lid' in valid_data:
            assert obj.lid == valid_data['lid']
        else:
            assert obj.lid is None

        if 'attributes' in valid_data:
            assert obj.attributes == valid_data['attributes']
        else:
            assert obj.attributes is None

        if 'relationships' in valid_data:
            assert obj.relationships == valid_data['relationships']
        else:
            assert obj.relationships is None

        if 'links' in valid_data:
            assert obj.links == valid_data['links']
        else:
            assert obj.links is None

        if 'meta' in valid_data:
            assert obj.meta == valid_data['meta']
        else:
            assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for additional valid data {valid_data}: {e}')


def test_resource_object_conflicting_attribute_relationship_names():
    """Test that attribute and relationship names do not conflict and do not include reserved keys."""
    data = {
        'type': 'projects',
        'id': 'proj1',
        'attributes': {'name': 'Project Alpha', 'description': 'An AI project.'},
        'relationships': {'name': RelationshipObject(data=ResourceIdentifierObject(type='names', id='name1'))},
    }
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Attribute and relationship names must not conflict. Conflicting names: {'name'}"
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_links_with_valid_and_invalid_entries():
    """Test that 'links' can contain both valid and invalid entries."""
    data = {
        'type': 'articles',
        'id': '1',
        'links': {'self': 'https://example.com/articles/1', 'related': 'invalid-uri'},
    }
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Link 'related' must be a valid URI-reference."
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_attributes_with_foreign_keys():
    """Test that attributes containing foreign keys are invalid."""
    data = {'type': 'posts', 'id': 'post1', 'attributes': {'title': 'Post Title', 'author_id': 'author1'}}
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Attribute names {'author_id'} are reserved for relationships and should not appear in attributes."
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_invalid_relationships_content():
    """Test that relationships contain only RelationshipObject instances."""
    data = {'type': 'articles', 'id': '1', 'relationships': {'author': 'not-a-relationship-object'}}
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = 'Input should be a valid dictionary or instance of RelationshipObject'
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message containing '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_unique_lid():
    """Test that 'lid' is unique within the document."""
    # Assuming uniqueness is handled outside the model, as model doesn't track all lids
    # Therefore, this test may not be applicable unless uniqueness is enforced within the model
    # If enforced, include the test; otherwise, skip or mock the behavior
    pass  # Placeholder for actual implementation if uniqueness is enforced


def test_resource_object_empty_strings():
    """Test behavior with empty strings for 'type', 'id', and 'lid'."""
    # 'type' is a NonEmptyStr with min_length=1, so empty string should fail
    data = {'type': '', 'id': '1'}
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Value error, 'type' must be a string."
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message containing '{expected_error}' not found in actual errors {actual_errors}"

    # 'id' as empty string should fail
    data = {'type': 'users', 'id': ''}
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Value error, 'id' must be a string."
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message containing '{expected_error}' not found in actual errors {actual_errors}"

    # 'lid' as empty string should fail
    data = {'type': 'users', 'lid': ''}
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Value error, 'lid' must be a string."
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message containing '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_extra_fields_not_allowed():
    """Test that extra fields are not allowed in ResourceObject."""
    data = {'type': 'articles', 'id': '1', 'extra_field': 'not allowed'}
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = 'extra_field'
    assert any(
        expected_error in error['loc'] for error in actual_errors
    ), f"Expected error message containing extra field '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_attributes_with_reserved_and_non_reserved_keys():
    """Test that attributes cannot include reserved keys even if other keys are valid."""
    data = {'type': 'articles', 'id': '1', 'attributes': {'title': 'Sample Article', 'id': 'should-not-be-allowed'}}
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Attribute names {'id'} are reserved and cannot be used."
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_relationships_with_reserved_and_non_reserved_keys():
    """Test that relationships cannot include reserved keys even if other keys are valid."""
    data = {
        'type': 'articles',
        'id': '1',
        'relationships': {
            'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='9')),
            'type': RelationshipObject(data=ResourceIdentifierObject(type='types', id='t1')),
        },
    }
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Relationship names {'type'} are reserved and cannot be used."
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_links_with_invalid_link_values():
    """Test that 'links' can contain only valid URIs or LinkObject instances."""
    data = {
        'type': 'articles',
        'id': '1',
        'links': {
            'self': 'https://example.com/articles/1',
            'related': 12345,  # Invalid type
        },
    }
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = 'Input should be a valid string'
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_resource_object_attributes_and_relationships_with_conflicting_keys():
    """Test that attributes and relationships do not have conflicting keys."""
    data = {
        'type': 'projects',
        'id': 'proj1',
        'attributes': {'name': 'Project Alpha', 'description': 'An AI project.'},
        'relationships': {
            'description': RelationshipObject(data=ResourceIdentifierObject(type='descriptions', id='desc1'))
        },
    }
    with pytest.raises(ValidationError) as exc_info:
        ResourceObject(**data)

    actual_errors = exc_info.value.errors()
    expected_error = "Attribute and relationship names must not conflict. Conflicting names: {'description'}"
    assert any(
        expected_error in error['msg'] for error in actual_errors
    ), f"Expected error message '{expected_error}' not found in actual errors {actual_errors}"


def test_from_model():
    class MockBaseModel(BaseModel):
        __type__ = 'mock_base_model'

        foo: str
        bar: int
        baz: bool

    mock_data = {'foo': 'hello', 'bar': 123, 'baz': True}

    try:
        obj = ResourceObject.from_model(MockBaseModel(**mock_data), id_='1')
        assert obj.type_ == 'mock_base_model'
        assert obj.id_ == '1'
        assert obj.lid is None
        assert obj.attributes == mock_data
        assert obj.relationships is None
        assert obj.links is None
        assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly when creating ResourceObject from model: {e}')


def test_from_model_missing_type():
    class InvalidMockBaseModel(BaseModel):
        foo: str
        bar: int
        baz: bool

    mock_data = {'foo': 'hello', 'bar': 123, 'baz': True}

    with pytest.raises(ValueError) as exc_info:
        _ = ResourceObject.from_model(InvalidMockBaseModel(**mock_data), id_='1')

    expected_error = "Resource 'type' must be provided either as a parameter or via '__type__'"
    assert expected_error in str(exc_info), f"Expected error message '{expected_error}' not found in error {exc_info}"
