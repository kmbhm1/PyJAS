from pydantic import ValidationError
from pyjas.v1_1.jsonapi_builder import (
    validate_member_name,
    ResourceIdentifierObject,
    LinkObject,
    LinkValue,
    RelationshipObject,
    ResourceObject,
    PrimaryData,
    ALLOWED_JSONAPI_VERSIONS,
    JSONAPIObject,
    Document,
)

import pytest


# validate_member_name tests

# Define the reserved characters as per the validate_member_name function
RESERVED_CHARACTERS = set('+.,[]!"#$%&\'()*/:;<=>?@\\^`{|}~\x7f')


@pytest.mark.parametrize(
    'valid_name',
    [
        # Core member names
        'user',
        'User123',
        'valid_name',
        'valid-name',
        'Valid Name',
        'ユーザー',  # Unicode characters
        '名',  # Single Unicode character'
        # @-Members
        '@meta',
        '@custom_member',
        '@Valid-Name',
        '@ユーザー',
        # Names with U+0080 and above
        'user\u0081',
        '用户',  # Chinese characters
        'مستخدم',  # Arabic characters
    ],
)
def test_validate_member_name_valid(valid_name):
    """Test that valid member names do not raise an exception."""
    try:
        validate_member_name(valid_name)
    except ValueError as e:
        pytest.fail(f"validate_member_name() raised ValueError unexpectedly for '{valid_name}': {e}")


@pytest.mark.parametrize(
    'invalid_name, error_message',
    [
        # Non-string inputs
        (123, 'Member name must be a string.'),
        (None, 'Member name must be a string.'),
        (['list'], 'Member name must be a string.'),
        ({'key': 'value'}, 'Member name must be a string.'),
        (True, 'Member name must be a string.'),
        # Empty string
        ('', 'Member name must contain at least one character.'),
        # Names containing reserved characters
        ('user+', "Invalid member name 'user+' according to JSON:API specification."),
        ('user.', "Invalid member name 'user.' according to JSON:API specification."),
        ('user[', "Invalid member name 'user[' according to JSON:API specification."),
        ('user]', "Invalid member name 'user]' according to JSON:API specification."),
        ('user"', "Invalid member name 'user\"' according to JSON:API specification."),
        ('user#', "Invalid member name 'user#' according to JSON:API specification."),
        ('user$', "Invalid member name 'user$' according to JSON:API specification."),
        ('user%', "Invalid member name 'user%' according to JSON:API specification."),
        ('user&', "Invalid member name 'user&' according to JSON:API specification."),
        ("user'", "Invalid member name 'user'' according to JSON:API specification."),
        ('user(', "Invalid member name 'user(' according to JSON:API specification."),
        ('user)', "Invalid member name 'user)' according to JSON:API specification."),
        ('user*', "Invalid member name 'user*' according to JSON:API specification."),
        ('user/', "Invalid member name 'user/' according to JSON:API specification."),
        ('user:', "Invalid member name 'user:' according to JSON:API specification."),
        ('user;', "Invalid member name 'user;' according to JSON:API specification."),
        ('user<', "Invalid member name 'user<' according to JSON:API specification."),
        ('user=', "Invalid member name 'user=' according to JSON:API specification."),
        ('user>', "Invalid member name 'user>' according to JSON:API specification."),
        ('user?', "Invalid member name 'user?' according to JSON:API specification."),
        ('user@', "Invalid member name 'user@' according to JSON:API specification."),
        ('user\\', "Invalid member name 'user\\' according to JSON:API specification."),
        ('user^', "Invalid member name 'user^' according to JSON:API specification."),
        ('user`', "Invalid member name 'user`' according to JSON:API specification."),
        ('user{', "Invalid member name 'user{' according to JSON:API specification."),
        ('user|', "Invalid member name 'user|' according to JSON:API specification."),
        ('user}', "Invalid member name 'user}' according to JSON:API specification."),
        ('user~', "Invalid member name 'user~' according to JSON:API specification."),
        ('user\x7f', "Invalid member name 'user\x7f' according to JSON:API specification."),
        # Invalid patterns
        ('-user', "Invalid member name '-user' according to JSON:API specification."),
        ('user-', "Invalid member name 'user-' according to JSON:API specification."),
        ('@-user', "Invalid member name '@-user' according to JSON:API specification."),
        ('ns:-member', "Invalid member name 'ns:-member' according to JSON:API specification."),
        ('ns:member-', "Invalid member name 'ns:member-' according to JSON:API specification."),
        # Extension Members are not valid member names
        ('ns:member', "Member name 'ns:member' contains reserved character ':' which is not allowed."),
        (
            'namespace:member_name',
            "Member name 'namespace:member_name' contains reserved character ':' which is not allowed.",
        ),
        (
            'namespace:Invalid-Name',
            "Member name 'namespace:Invalid-Name' contains reserved character ':' which is not allowed.",
        ),
        (
            '名前空間:メンバー',
            "Member name '名前空間:メンバー' contains reserved character ':' which is not allowed.",
        ),  # Namespace and member with Unicode
        ('@user@', "Invalid member name '@user@' according to JSON:API specification."),
        (':member', "Invalid member name ':member' according to JSON:API specification."),
        # Names with multiple reserved characters
        ('user+name', "Invalid member name 'user+name' according to JSON:API specification."),
        ('@user:name!', "Invalid member name '@user:name!' according to JSON:API specification."),
    ],
)
def test_validate_member_name_invalid(invalid_name, error_message):
    """Test that invalid member names raise a ValueError with the correct message."""
    with pytest.raises(ValueError) as exc_info:
        validate_member_name(invalid_name)
    assert str(exc_info.value) == error_message


def test_validate_member_name_reserved_del():
    """Test that the DEL character (U+007F) is not allowed."""
    name_with_del = 'user\x7fname'
    with pytest.raises(ValueError) as exc_info:
        validate_member_name(name_with_del)
    assert str(exc_info.value) == f"Invalid member name '{name_with_del}' according to JSON:API specification."


def test_validate_member_name_whitespace():
    """Test that leading and trailing spaces are handled correctly."""
    valid_name = ' user '
    with pytest.raises(ValueError) as exc_info:
        validate_member_name(valid_name)
    assert str(exc_info.value) == f"Invalid member name '{valid_name}' according to JSON:API specification."


def test_validate_member_name_only_allowed_special_chars():
    """Test names that consist solely of allowed internal characters."""
    with pytest.raises(ValueError) as exc_info:
        validate_member_name('-')
    assert str(exc_info.value) == "Invalid member name '-' according to JSON:API specification."

    with pytest.raises(ValueError) as exc_info:
        validate_member_name('_')
    assert str(exc_info.value) == "Invalid member name '_' according to JSON:API specification."

    with pytest.raises(ValueError) as exc_info:
        validate_member_name(' ')
    assert str(exc_info.value) == "Invalid member name ' ' according to JSON:API specification."


def test_validate_member_name_unicode_below_u0080():
    """Test that characters below U+0080 but not in reserved are allowed."""
    # Characters like accented letters
    valid_name = 'café'
    try:
        validate_member_name(valid_name)
    except ValueError as e:
        pytest.fail(f"validate_member_name() raised ValueError unexpectedly for '{valid_name}': {e}")


def test_validate_member_name_extension_without_namespace():
    """Test that extension members must have a namespace."""
    invalid_name = ':member'
    with pytest.raises(ValueError) as exc_info:
        validate_member_name(invalid_name)
    assert str(exc_info.value) == f"Invalid member name '{invalid_name}' according to JSON:API specification."


def test_validate_member_name_multiple_colons():
    """Test that multiple colons are not allowed in extension members."""
    invalid_name = 'ns:subns:member'
    with pytest.raises(ValueError) as exc_info:
        validate_member_name(invalid_name)
    assert str(exc_info.value) == f"Invalid member name '{invalid_name}' according to JSON:API specification."


# ResourceIdentifierObject tests


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


# LinkObject tests


@pytest.mark.parametrize(
    'valid_data',
    [
        # Only required 'href'
        {'href': 'https://example.com'},
        {'href': 'http://localhost:8000/api/resource'},
        # 'href' with all optional fields
        {
            'href': 'https://example.com/resource/1',
            'rel': 'self',
            'describedby': 'https://example.com/schema/resource',
            'title': 'Resource Title',
            'type': 'application/json',
            'hreflang': 'en',
            'meta': {'version': '1.0', 'author': 'John Doe'},
        },
        # 'hreflang' as a valid string
        {'href': 'https://example.com/resource/2', 'hreflang': 'fr'},
        # 'hreflang' as a list of valid strings
        {'href': 'https://example.com/resource/3', 'hreflang': ['en', 'es', 'de']},
        # Unicode characters in fields
        {
            'href': 'https://例子.测试',
            'rel': '自我',
            'describedby': 'https://例子.测试/架构',
            'title': '资源标题',
            'type': '应用/JSON',
            'hreflang': 'zh',
            'meta': {'版本': '1.0', '作者': '张三'},
        },
        # 'meta' with various data types
        {
            'href': 'https://example.com/resource/4',
            'meta': {'count': 10, 'tags': ['python', 'testing'], 'active': True, 'details': {'key': 'value'}},
        },
        # 'hreflang' with complex valid language tags
        {'href': 'https://example.com/resource/5', 'hreflang': ['en-US', 'pt-BR', 'zh-CN']},
    ],
)
def test_link_object_valid(valid_data):
    """Test that valid LinkObject instances are created successfully."""
    try:
        for k, v in valid_data.items():
            print(f'{k}: {v} ({type(v)})')
        obj = LinkObject(**valid_data)
        assert obj.href == valid_data['href']
        assert obj.rel == valid_data.get('rel')
        assert obj.describedby == valid_data.get('describedby')
        assert obj.title == valid_data.get('title')
        assert obj.type_ == valid_data.get('type')
        assert obj.hreflang == valid_data.get('hreflang')
        assert obj.meta == valid_data.get('meta')
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_errors',
    [
        # Missing required 'href'
        ({}, [{'loc': ('href',), 'msg': 'field required', 'type': 'value_error.missing'}]),
        # 'href' as invalid URL
        (
            {'href': 'not-a-valid-url'},
            [{'loc': ('href',), 'msg': 'invalid or missing URL scheme', 'type': 'value_error.url.scheme'}],
        ),
        # 'describedby' as invalid URL
        (
            {'href': 'https://example.com', 'describedby': 'invalid-url'},
            [{'loc': ('describedby',), 'msg': 'invalid or missing URL scheme', 'type': 'value_error.url.scheme'}],
        ),
        # 'rel' as non-string
        (
            {'href': 'https://example.com', 'rel': 123},
            [{'loc': ('rel',), 'msg': 'str type expected', 'type': 'type_error.str'}],
        ),
        # 'rel' with non-alphanumeric characters
        (
            {'href': 'https://example.com', 'rel': 'self-link'},
            [
                {
                    'loc': ('rel',),
                    'msg': "'rel' must be a valid link relation type (alphanumeric characters only).",
                    'type': 'value_error',
                }
            ],
        ),
        # 'type_' as non-string
        (
            {'href': 'https://example.com', 'type': 456},
            [{'loc': ('type_',), 'msg': 'str type expected', 'type': 'type_error.str'}],
        ),
        # 'hreflang' as invalid string
        (
            {'href': 'https://example.com', 'hreflang': 'invalid-lang-tag'},
            [
                {
                    'loc': ('hreflang',),
                    'msg': "'hreflang' must be a valid language tag. Got: invalid-lang-tag",
                    'type': 'value_error',
                }
            ],
        ),
        # 'hreflang' as list containing invalid string
        (
            {'href': 'https://example.com', 'hreflang': ['en', 'invalid-lang-tag']},
            [
                {
                    'loc': ('hreflang',),
                    'msg': "'hreflang' must be a valid language tag. Got: invalid-lang-tag",
                    'type': 'value_error',
                }
            ],
        ),
        # 'hreflang' as list containing non-string
        (
            {'href': 'https://example.com', 'hreflang': ['en', 123]},
            [
                {
                    'loc': ('hreflang', 1),
                    'msg': "Each 'hreflang' entry must be a string. Got: 123",
                    'type': 'value_error',
                }
            ],
        ),
        # 'hreflang' as unsupported type
        (
            {'href': 'https://example.com', 'hreflang': {'lang': 'en'}},
            [{'loc': ('hreflang',), 'msg': "'hreflang' must be a string or a list of strings.", 'type': 'value_error'}],
        ),
        # 'meta' as non-dictionary
        (
            {'href': 'https://example.com', 'meta': 'not-a-dict'},
            [{'loc': ('meta',), 'msg': 'value is not a valid dict', 'type': 'type_error.dict'}],
        ),
        # 'title' as non-string
        (
            {'href': 'https://example.com', 'title': 789},
            [{'loc': ('title',), 'msg': 'str type expected', 'type': 'type_error.str'}],
        ),
        # 'hreflang' as empty list
        (
            {'href': 'https://example.com', 'hreflang': []},
            [{'loc': ('hreflang',), 'msg': "'hreflang' must be a valid language tag. Got: ", 'type': 'value_error'}],
        ),
        # 'hreflang' as empty string
        (
            {'href': 'https://example.com', 'hreflang': ''},
            [{'loc': ('hreflang',), 'msg': "'hreflang' must be a valid language tag. Got: ", 'type': 'value_error'}],
        ),
        # 'hreflang' as list with empty string
        (
            {'href': 'https://example.com', 'hreflang': ['en', '']},
            [{'loc': ('hreflang', 1), 'msg': "'hreflang' must be a valid language tag. Got: ", 'type': 'value_error'}],
        ),
        # 'meta' as list instead of dict
        (
            {'href': 'https://example.com', 'meta': ['not', 'a', 'dict']},
            [{'loc': ('meta',), 'msg': 'value is not a valid dict', 'type': 'type_error.dict'}],
        ),
        # Extra unexpected field
        (
            {'href': 'https://example.com', 'extra': 'field'},
            [{'loc': ('extra',), 'msg': 'extra fields not permitted', 'type': 'value_error.extra'}],
        ),
    ],
)
def test_link_object_invalid(invalid_data, expected_errors):
    """Test that invalid LinkObject instances raise ValidationError with correct messages."""
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**invalid_data)

    # Extract actual errors
    actual_errors = exc_info.value.errors()

    # Check each expected error is in actual errors
    for expected_error in expected_errors:
        assert expected_error in actual_errors, f'Expected error {expected_error} not found in {actual_errors}'


def test_link_object_meta_optional():
    """Test that 'meta' is optional."""
    data = {'href': 'https://example.com/resource'}
    try:
        obj = LinkObject(**data)
        assert obj.meta is None
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly: {e}')


def test_link_object_alias():
    """Test that alias 'type_' works correctly."""
    data = {'href': 'https://example.com/resource', 'type': 'application/json'}
    obj = LinkObject(**data)
    assert obj.type_ == 'application/json'
    # Test accessing via alias in dict
    assert obj.dict(by_alias=True)['type'] == 'application/json'


def test_link_object_extra_fields():
    """Test that extra fields are not allowed unless configured otherwise."""
    data = {'href': 'https://example.com/resource', 'rel': 'self', 'unknown_field': 'should fail'}
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)
    assert any(
        error['loc'] == ('unknown_field',) for error in exc_info.value.errors()
    ), 'Expected error for unknown_field not found.'


def test_link_object_empty_strings():
    """Test behavior with empty strings for optional fields."""
    data = {
        'href': 'https://example.com/resource',
        'rel': '',
        'title': '',
        'type': '',
        'hreflang': '',
    }
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    # Check for 'rel' being empty but still a valid alphanumeric string (empty string may fail)
    # Depending on implementation, empty string might fail alphanumeric check
    expected_error = {
        'loc': ('rel',),
        'msg': "'rel' must be a valid link relation type (alphanumeric characters only). Got: ",
        'type': 'value_error',
    }
    assert expected_error in exc_info.value.errors(), "Expected error for empty 'rel' not found."


def test_link_object_valid_hreflang_complex_tags():
    """Test 'hreflang' with complex valid language tags."""
    data = {'href': 'https://example.com/resource', 'hreflang': ['en-US', 'pt-BR', 'zh-Hans']}
    try:
        obj = LinkObject(**data)
        assert obj.hreflang == ['en-US', 'pt-BR', 'zh-Hans']
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for complex hreflang: {e}')


def test_link_object_invalid_hreflang_complex_tags():
    """Test 'hreflang' with complex invalid language tags."""
    data = {'href': 'https://example.com/resource', 'hreflang': ['en-US', 'invalid-tag', 'zh-Hans']}
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    expected_error = {
        'loc': ('hreflang', 1),
        'msg': "'hreflang' must be a valid language tag. Got: invalid-tag",
        'type': 'value_error',
    }
    assert expected_error in exc_info.value.errors(), 'Expected error for invalid hreflang tag not found.'


def test_link_object_invalid_rel_characters():
    """Test that 'rel' must contain only alphanumeric characters."""
    data = {
        'href': 'https://example.com/resource',
        'rel': 'self-link',  # Contains hyphen, which is invalid as per the validator
    }
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    expected_error = {
        'loc': ('rel',),
        'msg': "'rel' must be a valid link relation type (alphanumeric characters only).",
        'type': 'value_error',
    }
    assert expected_error in exc_info.value.errors(), "Expected error for non-alphanumeric 'rel' not found."


def test_link_object_invalid_type_non_string():
    """Test that 'type_' must be a string."""
    data = {'href': 'https://example.com/resource', 'type': 123}
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    expected_error = {'loc': ('type_',), 'msg': 'str type expected', 'type': 'type_error.str'}
    assert expected_error in exc_info.value.errors(), "Expected error for non-string 'type_' not found."


def test_link_object_invalid_hreflang_type():
    """Test that 'hreflang' must be string or list of strings."""
    data = {
        'href': 'https://example.com/resource',
        'hreflang': 123,  # Invalid type
    }
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    expected_error = {
        'loc': ('hreflang',),
        'msg': "'hreflang' must be a string or a list of strings.",
        'type': 'value_error',
    }
    assert expected_error in exc_info.value.errors(), "Expected error for invalid 'hreflang' type not found."


def test_link_object_hreflang_empty_list():
    """Test that 'hreflang' as an empty list is invalid."""
    data = {'href': 'https://example.com/resource', 'hreflang': []}
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    # Depending on validator, it might raise an error for each empty string in list or for the list itself
    expected_error = {
        'loc': ('hreflang',),
        'msg': "'hreflang' must be a valid language tag. Got: ",
        'type': 'value_error',
    }
    # Alternatively, if list is empty, it might not raise specific hreflang errors but still allow it
    # Adjust the expected behavior based on actual validator implementation
    assert any(
        error['loc'] == ('hreflang',) for error in exc_info.value.errors()
    ), "Expected error for empty 'hreflang' list not found."


def test_link_object_extra_fields_allowed_if_configured():
    """Test that extra fields are allowed if the model is configured to allow them."""
    # This test assumes that LinkObject does not allow extra fields.
    # If you have configured LinkObject to allow extra fields, adjust accordingly.
    data = {'href': 'https://example.com/resource', 'extra_field': 'extra_value'}
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)
    assert any(
        error['loc'] == ('extra_field',) for error in exc_info.value.errors()
    ), 'Expected error for extra_field not found.'


def test_link_object_valid_rel_alphanumeric():
    """Test that 'rel' with only alphanumeric characters is valid."""
    data = {'href': 'https://example.com/resource', 'rel': 'self123'}
    try:
        obj = LinkObject(**data)
        assert obj.rel == 'self123'
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly for valid 'rel': {e}")


def test_link_object_invalid_hreflang_non_string_in_list():
    """Test that 'hreflang' list containing non-string raises error."""
    data = {'href': 'https://example.com/resource', 'hreflang': ['en', 456, 'fr']}
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    expected_error = {
        'loc': ('hreflang', 1),
        'msg': "Each 'hreflang' entry must be a string. Got: 456",
        'type': 'value_error',
    }
    assert (
        expected_error in exc_info.value.errors()
    ), "Expected error for non-string entry in 'hreflang' list not found."


def test_link_object_valid_empty_meta():
    """Test that 'meta' can be an empty dictionary."""
    data = {'href': 'https://example.com/resource', 'meta': {}}
    try:
        obj = LinkObject(**data)
        assert obj.meta == {}
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly for empty 'meta': {e}")


def test_link_object_invalid_meta_nested_non_dict():
    """Test that 'meta' containing nested non-dict raises error."""
    data = {'href': 'https://example.com/resource', 'meta': {'key': ['list', 'of', 'values']}}
    try:
        obj = LinkObject(**data)
        assert obj.meta == {'key': ['list', 'of', 'values']}
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly for nested 'meta': {e}")


def test_link_object_invalid_type_special_characters():
    """Test that 'type_' with special characters is allowed if it's a string."""
    data = {'href': 'https://example.com/resource', 'type': 'application/vnd.api+json'}
    try:
        obj = LinkObject(**data)
        assert obj.type_ == 'application/vnd.api+json'
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly for 'type_' with special characters: {e}")
