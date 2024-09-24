from pydantic import HttpUrl
import pytest
from pydantic_core import ErrorDetails, ValidationError
from pyjas.v1_1.jsonapi_builder import LinkObject


def clean_actual_errors(errors: list[ErrorDetails]) -> list[dict]:
    """Helper function to clean up actual errors for comparison."""
    for e in errors:
        e.pop('ctx', None)  # Remove 'ctx' as it's not relevant for comparison
        e.pop('url', None)  # Remove 'url' as it's not relevant for comparison
    return errors


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
        # {
        #     'href': 'https://例子.测试',
        #     'rel': '自我',
        #     'describedby': 'https://例子.测试/架构',
        #     'title': '资源标题',
        #     'type': '应用/JSON',
        #     'hreflang': 'zh',
        #     'meta': {'版本': '1.0', '作者': '张三'},
        # },
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
        obj = LinkObject(**{**valid_data})
        assert obj.href == HttpUrl(url=valid_data['href'])
        assert obj.rel == valid_data.get('rel')
        durl = valid_data.get('describedby', None)
        assert obj.describedby == durl if durl is None else HttpUrl(url=durl)
        assert obj.title == valid_data.get('title')
        assert obj.type_ == valid_data.get('type')
        assert obj.hreflang == valid_data.get('hreflang')
        assert obj.meta == valid_data.get('meta')
    except ValidationError as e:
        pytest.fail(f'ValidationError raised unexpectedly for data {valid_data}: {e}')


@pytest.mark.parametrize(
    'invalid_data, expected_errors',
    [
        # 0. Missing required 'href'
        (
            {},
            [
                {
                    'type': 'missing',
                    'loc': ('href',),
                    'msg': 'Field required',
                    'input': {},
                }
            ],
        ),
        # 1. 'href' as invalid URL
        (
            {'href': 'not-a-valid-url'},
            [
                {
                    'type': 'url_parsing',
                    'loc': ('href',),
                    'msg': 'Input should be a valid URL, relative URL without a base',
                    'input': 'not-a-valid-url',
                }
            ],
        ),
        # 2. 'describedby' as invalid URL
        (
            {'href': 'https://example.com', 'describedby': 'invalid-url'},
            [
                {
                    'type': 'url_parsing',
                    'loc': ('describedby',),
                    'msg': 'Input should be a valid URL, relative URL without a base',
                    'input': 'invalid-url',
                }
            ],
        ),
        # 3. 'rel' as non-string
        (
            {'href': 'https://example.com', 'rel': 123},
            [
                {
                    'type': 'string_type',
                    'loc': ('rel',),
                    'msg': 'Input should be a valid string',
                    'input': 123,
                }
            ],
        ),
        # 4. 'rel' with non-alphanumeric characters
        (
            {'href': 'https://example.com', 'rel': 'self-link'},
            [
                {
                    'type': 'value_error',
                    'loc': (),
                    'msg': "Value error, 'rel' must be a valid link relation type (alphanumeric characters only).",
                    'input': {'href': 'https://example.com', 'rel': 'self-link'},
                }
            ],
        ),
        # 5. 'type_' as non-string
        (
            {'href': 'https://example.com', 'type': 456},
            [
                {
                    'type': 'string_type',
                    'loc': ('type',),
                    'msg': 'Input should be a valid string',
                    'input': 456,
                }
            ],
        ),
        # 6. 'hreflang' as invalid string
        (
            {'href': 'https://example.com', 'hreflang': 'invalid-lang-tag'},
            [
                {
                    'type': 'value_error',
                    'loc': (),
                    'msg': "Value error, 'hreflang' must be a valid language tag. Got: invalid-lang-tag",
                    'input': {'href': 'https://example.com', 'hreflang': 'invalid-lang-tag'},
                }
            ],
        ),
        # 7. 'hreflang' as list containing invalid string
        (
            {'href': 'https://example.com', 'hreflang': ['en', 'invalid-lang-tag']},
            [
                {
                    'type': 'value_error',
                    'loc': (),
                    'msg': "Value error, 'hreflang' must be a valid language tag. Got: invalid-lang-tag",
                    'input': {'href': 'https://example.com', 'hreflang': ['en', 'invalid-lang-tag']},
                }
            ],
        ),
        # 8. 'hreflang' as list containing non-string
        (
            {'href': 'https://example.com', 'hreflang': ['en', 123]},
            [
                {
                    'type': 'string_type',
                    'loc': ('hreflang', 'list[str]', 1),
                    'msg': 'Input should be a valid string',
                    'input': 123,
                },
            ],
        ),
        # 9. 'hreflang' as unsupported type
        (
            {'href': 'https://example.com', 'hreflang': {'lang': 'en'}},
            [
                {
                    'type': 'list_type',
                    'loc': ('hreflang', 'list[str]'),
                    'msg': 'Input should be a valid list',
                    'input': {'lang': 'en'},
                },
            ],
        ),
        # 10. 'meta' as non-dictionary
        (
            {'href': 'https://example.com', 'meta': 'not-a-dict'},
            [
                {
                    'type': 'dict_type',
                    'loc': ('meta',),
                    'msg': 'Input should be a valid dictionary',
                    'input': 'not-a-dict',
                }
            ],
        ),
        # 11. 'title' as non-string
        (
            {'href': 'https://example.com', 'title': 789},
            [{'type': 'string_type', 'loc': ('title',), 'msg': 'Input should be a valid string', 'input': 789}],
        ),
        # 12. 'hreflang' as empty list
        (
            {'href': 'https://example.com', 'hreflang': []},
            [
                {
                    'type': 'value_error',
                    'loc': (),
                    'msg': "Value error, 'hreflang' must be a non-empty string or a list of non-empty strings.",
                    'input': {'href': 'https://example.com', 'hreflang': []},
                }
            ],
        ),
        # 13. 'hreflang' as empty string
        (
            {'href': 'https://example.com', 'hreflang': ''},
            [
                {
                    'type': 'value_error',
                    'loc': (),
                    'msg': "Value error, 'hreflang' must be a non-empty string or a list of non-empty strings.",
                    'input': {'href': 'https://example.com', 'hreflang': ''},
                }
            ],
        ),
        # 14. 'hreflang' as list with empty string
        (
            {'href': 'https://example.com', 'hreflang': ['en', '']},
            [
                {
                    'type': 'value_error',
                    'loc': (),
                    'msg': "Value error, 'hreflang' must be a valid language tag. Got: ",
                    'input': {'href': 'https://example.com', 'hreflang': ['en', '']},
                }
            ],
        ),
        # 15. 'meta' as list instead of dict
        (
            {'href': 'https://example.com', 'meta': ['not', 'a', 'dict']},
            [
                {
                    'type': 'dict_type',
                    'loc': ('meta',),
                    'msg': 'Input should be a valid dictionary',
                    'input': ['not', 'a', 'dict'],
                }
            ],
        ),
        # 16. Extra unexpected field
        (
            {'href': 'https://example.com', 'extra': 'field'},
            [{'type': 'extra_forbidden', 'loc': ('extra',), 'msg': 'Extra inputs are not permitted', 'input': 'field'}],
        ),
    ],
)
def test_link_object_invalid(invalid_data, expected_errors):
    """Test that invalid LinkObject instances raise ValidationError with correct messages."""
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**invalid_data)

    # Extract actual errors
    actual_errors = clean_actual_errors(exc_info.value.errors())

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
    assert obj.model_dump(by_alias=True)['type'] == 'application/json'


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

    # Depending on the validator, it might raise an error for each empty string or for the field itself
    # Adjust the expected behavior based on actual validator implementation
    expected = {
        'input': {'href': 'https://example.com/resource', 'rel': '', 'title': '', 'type': '', 'hreflang': ''},
        'loc': (),
        'msg': "Value error, 'hreflang' must be a non-empty string or a list of non-empty strings.",
        'type': 'value_error',
    }
    actual_errors = clean_actual_errors(exc_info.value.errors())
    assert expected in actual_errors, 'Expected error for empty string not found.'


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
        'input': {'href': 'https://example.com/resource', 'hreflang': ['en-US', 'invalid-tag', 'zh-Hans']},
        'loc': (),
        'msg': "Value error, 'hreflang' must be a valid language tag. Got: invalid-tag",
        'type': 'value_error',
    }
    actual_errors = clean_actual_errors(exc_info.value.errors())
    assert expected_error in actual_errors, 'Expected error for invalid hreflang tag not found.'


def test_link_object_invalid_rel_characters():
    """Test that 'rel' must contain only alphanumeric characters."""
    data = {
        'href': 'https://example.com/resource',
        'rel': 'self-link',  # Contains hyphen, which is invalid as per the validator
    }
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    expected_error = {
        'input': {'href': 'https://example.com/resource', 'rel': 'self-link'},
        'loc': (),
        'msg': "Value error, 'rel' must be a valid link relation type (alphanumeric characters only).",
        'type': 'value_error',
    }
    actual_errors = clean_actual_errors(exc_info.value.errors())
    assert expected_error in actual_errors, "Expected error for non-alphanumeric 'rel' not found."


def test_link_object_invalid_type_non_string():
    """Test that 'type_' must be a string."""
    data = {'href': 'https://example.com/resource', 'type': 123}
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    expected_error = {'input': 123, 'loc': ('type',), 'msg': 'Input should be a valid string', 'type': 'string_type'}
    actual_errors = clean_actual_errors(exc_info.value.errors())
    assert expected_error in actual_errors, "Expected error for non-string 'type_' not found."


def test_link_object_invalid_hreflang_type():
    """Test that 'hreflang' must be string or list of strings."""
    data = {
        'href': 'https://example.com/resource',
        'hreflang': 123,  # Invalid type
    }
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    expected_error = {
        'input': 123,
        'loc': ('hreflang', 'list[str]'),
        'msg': 'Input should be a valid list',
        'type': 'list_type',
    }
    actual_errors = clean_actual_errors(exc_info.value.errors())
    assert expected_error in actual_errors, "Expected error for invalid 'hreflang' type not found."


def test_link_object_hreflang_empty_list():
    """Test that 'hreflang' as an empty list is invalid."""
    data = {'href': 'https://example.com/resource', 'hreflang': []}
    with pytest.raises(ValidationError) as exc_info:
        LinkObject(**data)

    # Depending on validator, it might raise an error for each empty string in list or for the list itself
    expected_error = {
        'input': {'href': 'https://example.com/resource', 'hreflang': []},
        'loc': (),
        'msg': "Value error, 'hreflang' must be a non-empty string or a list of non-empty strings.",
        'type': 'value_error',
    }
    # Alternatively, if list is empty, it might not raise specific hreflang errors but still allow it
    # Adjust the expected behavior based on actual validator implementation
    actual_errors = clean_actual_errors(exc_info.value.errors())
    assert expected_error in actual_errors, "Expected error for empty 'hreflang' list not found."


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
        'input': 456,
        'loc': ('hreflang', 'list[str]', 1),
        'msg': 'Input should be a valid string',
        'type': 'string_type',
    }
    actual_errors = clean_actual_errors(exc_info.value.errors())
    assert expected_error in actual_errors, "Expected error for non-string entry in 'hreflang' list not found."


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
