from pydantic_core import ValidationError
from pyjas.v1_1.jsonapi_builder import ResourceIdentifierObject
import pytest


@pytest.mark.parametrize(
    'data',
    [
        # Valid instances with 'type' and 'id'
        {'type': 'articles', 'id': '1'},
        {'type': 'users', 'id': 'user123'},
        # Valid instances with 'type' and 'lid'
        {'type': 'comments', 'lid': 'local-456'},
        {'type': 'posts', 'lid': 'local-789'},
        # Valid instances with 'type', 'id', and 'lid'
        {'type': 'tags', 'id': 'tag1', 'lid': 'local-tag1'},
        {'type': 'categories', 'id': 'cat123', 'lid': 'local-cat123'},
        # Valid instances including 'meta'
        {'type': 'articles', 'id': '1', 'meta': {'created_at': '2024-01-01', 'updated_at': '2024-01-02'}},
        {'type': 'users', 'lid': 'local-user456', 'meta': {'role': 'admin'}},
        # Valid instances with Unicode characters
        {'type': '文章', 'id': '1'},  # "文章" means "article" in Chinese
        {
            'type': 'utilisateurs',
            'lid': 'local-用户789',
        },  # "utilisateurs" is French for "users", "用户" is Chinese for "user"
    ],
)
def test_resource_identifier_object_valid(data):
    """Test that valid ResourceIdentifierObject instances are created successfully."""
    try:
        obj = ResourceIdentifierObject(**data)
        assert obj.type_ == data['type']
        assert obj.id_ == data.get('id')
        assert obj.lid == data.get('lid')
        assert obj.meta == data.get('meta')
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data {data}: {e}')


@pytest.mark.parametrize(
    'data, error_message',
    [
        # Missing both 'id' and 'lid'
        ({'type': 'articles'}, "ResourceIdentifierObject must have either 'id' or 'lid'."),
        ({'type': 'users', 'meta': {'role': 'admin'}}, "ResourceIdentifierObject must have either 'id' or 'lid'."),
        # Non-string 'type'
        ({'type': 123, 'id': '1'}, "'type' must be a string."),
        ({'type': None, 'id': '1'}, "'type' must be a string."),
        ({'type': True, 'lid': 'local-123'}, "'type' must be a string."),
        # Non-string 'id'
        ({'type': 'articles', 'id': 456}, "'id' must be a string."),
        (
            {'type': 'users', 'id': None},
            "ResourceIdentifierObject must have either 'id' or 'lid'.",
        ),  # id is None and lid is missing
        ({'type': 'comments', 'id': True}, "'id' must be a string."),
        # Non-string 'lid'
        ({'type': 'posts', 'lid': 789}, "'lid' must be a string."),
        ({'type': 'categories', 'lid': False, 'id': 'cat123'}, "'lid' must be a string."),
        # 'meta' not a dictionary
        ({'type': 'articles', 'id': '1', 'meta': 'not-a-dict'}, 'value is not a valid dict'),
        ({'type': 'users', 'lid': 'local-456', 'meta': ['list', 'not', 'dict']}, 'value is not a valid dict'),
        # Additional invalid cases
        # ({'type': '', 'id': '1'}, None),  # Empty 'type' is allowed as long as it's a string
        # ({'type': ' ', 'id': '1'}, None),  # 'type' with space is allowed
        ({'type': 'articles', 'id': ''}, None),  # Empty 'id' is allowed (depending on specifications)
        ({'type': 'articles', 'lid': ''}, None),  # Empty 'lid' is allowed (depending on specifications)
        ({'type': 'articles', 'id': '', 'lid': ''}, "ResourceIdentifierObject must have either 'id' or 'lid'."),
    ],
)
def test_resource_identifier_object_invalid(data, error_message):
    """Test that invalid ResourceIdentifierObject instances raise ValidationError."""
    with pytest.raises(ValidationError):
        ResourceIdentifierObject(**data)


def test_resource_identifier_object_meta_optional():
    """Test that 'meta' is optional."""
    data = {'type': 'articles', 'id': '1'}
    try:
        obj = ResourceIdentifierObject(**data)
        assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly: {e}')


def test_resource_identifier_object_id_and_lid_both_present():
    """Test that both 'id' and 'lid' can be present."""
    data = {'type': 'articles', 'id': '1', 'lid': 'local-1', 'meta': {'source': 'internal'}}
    try:
        obj = ResourceIdentifierObject(**data)
        assert obj.id_ == '1'
        assert obj.lid == 'local-1'
        assert obj.meta == {'source': 'internal'}
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly: {e}')


def test_resource_identifier_object_empty_strings():
    """Test behavior with empty strings for 'type', 'id', and 'lid'."""
    # Assuming that empty strings are allowed for 'type', 'id', and 'lid' as long as they are strings
    # If the specification requires non-empty strings, additional validation should be added
    data = {'type': '', 'id': '1'}
    try:
        obj = ResourceIdentifierObject(**data)
        assert obj.type_ == ''
        assert obj.id_ == '1'
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly for empty 'type': {e}")

    data = {'type': 'articles', 'lid': ''}
    try:
        obj = ResourceIdentifierObject(**data)
    except ValidationError:
        pass
    else:
        pytest.fail("ValidationError expected for empty 'lid'")


def test_resource_identifier_object_extra_fields():
    """Test that extra fields are not allowed unless configured otherwise."""
    data = {'type': 'articles', 'id': '1', 'extra': 'field'}
    with pytest.raises(ValidationError) as exc_info:
        ResourceIdentifierObject(**data)
    assert 'extra' in str(exc_info.value)


def test_resource_identifier_object_alias():
    """Test that aliases ('type' -> 'type_', 'id' -> 'id_') work correctly."""
    data = {'type': 'articles', 'id': '1'}
    obj = ResourceIdentifierObject(**data)
    assert obj.type_ == 'articles'
    assert obj.id_ == '1'

    # Test accessing via alias
    assert obj.model_dump(by_alias=True, exclude_none=True) == data


def test_resource_identifier_object_partial_fields():
    """Test instances with partial fields."""
    # Only 'type' and 'id'
    data = {'type': 'articles', 'id': '1'}
    obj = ResourceIdentifierObject(**data)
    assert obj.type_ == 'articles'
    assert obj.id_ == '1'
    assert obj.lid is None
    assert obj.meta is None

    # Only 'type' and 'lid'
    data = {'type': 'articles', 'lid': 'local-1'}
    obj = ResourceIdentifierObject(**data)
    assert obj.type_ == 'articles'
    assert obj.id_ is None
    assert obj.lid == 'local-1'
    assert obj.meta is None

    # 'type', 'id', 'lid'
    data = {'type': 'articles', 'id': '1', 'lid': 'local-1'}
    obj = ResourceIdentifierObject(**data)
    assert obj.type_ == 'articles'
    assert obj.id_ == '1'
    assert obj.lid == 'local-1'
    assert obj.meta is None


def test_resource_identifier_object_invalid_meta_content():
    """Test that 'meta' can contain any non-standard meta-information."""
    # Valid 'meta' with various types of data
    data = {
        'type': 'articles',
        'id': '1',
        'meta': {
            'views': 100,
            'tags': ['python', 'testing'],
            'published': True,
            'ratings': {'average': 4.5, 'count': 10},
        },
    }
    try:
        obj = ResourceIdentifierObject(**data)
        assert obj.meta == data['meta']
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly for complex 'meta': {e}")


def test_resource_identifier_object_invalid_type_non_string_but_correct():
    """Test that 'type' is validated as string even with similar types."""
    data = {'type': '123', 'id': '1'}  # 'type' as numeric string is allowed
    try:
        obj = ResourceIdentifierObject(**data)
        assert obj.type_ == '123'
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly for numeric string 'type': {e}")
