# test_content_type.py

import pytest
from urllib.parse import urlparse
from pyjas.v1_1.content_negotiation import ContentType, ContentTypeError


# Sample valid URIs for testing
VALID_URI_1 = 'https://example.com/ext'
VALID_URI_2 = 'http://example.org/profile'
VALID_URI_3 = 'https://another.com/resource'

# Sample invalid URIs for testing
INVALID_URI_1 = 'not-a-valid-uri'
INVALID_URI_2 = 'ftp://'

# Test Cases for Parsing Content Type Strings


@pytest.mark.parametrize(
    'content_type_str, expected_media_type, expected_params',
    [
        ('application/vnd.api+json', 'application/vnd.api+json', {}),
        (
            'application/vnd.api+json; ext="https://example.com/ext"',
            'application/vnd.api+json',
            {'ext': ['https://example.com/ext']},
        ),
        (
            'application/vnd.api+json; profile="http://example.org/profile"',
            'application/vnd.api+json',
            {'profile': ['http://example.org/profile']},
        ),
        (
            'application/vnd.api+json; ext="https://example.com/ext1 https://example.com/ext2"; profile="http://example.org/profile1"',
            'application/vnd.api+json',
            {
                'ext': ['https://example.com/ext1', 'https://example.com/ext2'],
                'profile': ['http://example.org/profile1'],
            },
        ),
        (
            'application/vnd.api+json; profile="http://example.org/profile1 http://example.org/profile2"; ext="https://example.com/ext1"',
            'application/vnd.api+json',
            {
                'profile': ['http://example.org/profile1', 'http://example.org/profile2'],
                'ext': ['https://example.com/ext1'],
            },
        ),
        # Test with parameters in different order and extra spaces
        (
            'application/vnd.api+json;   profile="http://example.org/profile1" ; ext="https://example.com/ext1"',
            'application/vnd.api+json',
            {'profile': ['http://example.org/profile1'], 'ext': ['https://example.com/ext1']},
        ),
    ],
)
def test_parse_valid_content_type(content_type_str, expected_media_type, expected_params):
    ct = ContentType.parse(content_type_str)
    assert ct.media_type == expected_media_type
    assert ct.params == expected_params


# Test Parsing Invalid Content Type Strings


@pytest.mark.parametrize(
    'content_type_str, error_message',
    [
        ('', 'Content-Type header is empty.'),
        ('text/plain', "Invalid media type 'text/plain'. Expected 'application/vnd.api+json'."),
        (
            'application/vnd.api+json; unknown="value"',
            "Invalid parameter 'unknown'. Only 'ext' and 'profile' are allowed.",
        ),
        ('application/vnd.api+json; ext=invalid_uri', "Invalid URI in 'ext': 'invalid_uri'"),
        (
            'application/vnd.api+json; profile="http://valid.com" ; ext="invalid_uri"',
            "Invalid URI in 'ext': 'invalid_uri'",
        ),
        ('application/vnd.api+json; ext', "Invalid parameter format: 'ext'"),
        (
            'application/vnd.api+json; ext="https://valid.com"; extra="value"',
            "Invalid parameter 'extra'. Only 'ext' and 'profile' are allowed.",
        ),
        ('application/vnd.api+json; ext="https://valid.com invalid_uri"', "Invalid URI in 'ext': 'invalid_uri'"),
        ('application/vnd.api+json; profile="http://valid.com ftp://"', "Invalid URI in 'profile': 'ftp://'"),
    ],
)
def test_parse_invalid_content_type(content_type_str, error_message):
    with pytest.raises(ContentTypeError) as exc_info:
        ContentType.parse(content_type_str)
    assert str(exc_info.value) == error_message


# Test Validation in Constructor


def test_constructor_valid():
    params = {'ext': [VALID_URI_1, VALID_URI_3], 'profile': [VALID_URI_2]}
    ct = ContentType(media_type=ContentType.MEDIA_TYPE, params=params)
    assert ct.media_type == ContentType.MEDIA_TYPE
    assert ct.params == params


def test_constructor_invalid_media_type():
    with pytest.raises(ContentTypeError) as exc_info:
        ContentType(media_type='text/plain', params={})
    assert str(exc_info.value) == f"Invalid media type 'text/plain'. Expected '{ContentType.MEDIA_TYPE}'."


def test_constructor_invalid_parameter_key():
    params = {'unknown': ['https://example.com']}
    with pytest.raises(ContentTypeError) as exc_info:
        ContentType(media_type=ContentType.MEDIA_TYPE, params=params)
    assert str(exc_info.value) == "Invalid parameter 'unknown'. Only 'ext' and 'profile' are allowed."


def test_constructor_invalid_parameter_value_type():
    params = {'ext': 'https://example.com'}  # Should be a list
    with pytest.raises(ContentTypeError) as exc_info:
        ContentType(media_type=ContentType.MEDIA_TYPE, params=params)
    assert str(exc_info.value) == "The value of 'ext' must be a list of URIs."


def test_constructor_invalid_uri_in_params():
    params = {'ext': [VALID_URI_1, INVALID_URI_1]}
    with pytest.raises(ContentTypeError) as exc_info:
        ContentType(media_type=ContentType.MEDIA_TYPE, params=params)
    assert str(exc_info.value) == f"Invalid URI in 'ext': '{INVALID_URI_1}'"


# Test Properties


def test_extensions_property():
    params = {'ext': [VALID_URI_1, VALID_URI_3]}
    ct = ContentType(media_type=ContentType.MEDIA_TYPE, params=params)
    assert ct.extensions == [VALID_URI_1, VALID_URI_3]


def test_profiles_property():
    params = {'profile': [VALID_URI_2]}
    ct = ContentType(media_type=ContentType.MEDIA_TYPE, params=params)
    assert ct.profiles == [VALID_URI_2]


def test_extensions_property_empty():
    ct = ContentType(media_type=ContentType.MEDIA_TYPE, params={})
    assert ct.extensions == []


def test_profiles_property_empty():
    ct = ContentType(media_type=ContentType.MEDIA_TYPE, params={})
    assert ct.profiles == []


# Test Serialization with to_string


@pytest.mark.parametrize(
    'params, expected_str',
    [
        ({}, 'application/vnd.api+json'),
        ({'ext': ['https://example.com/ext1']}, 'application/vnd.api+json; ext="https://example.com/ext1"'),
        (
            {'profile': ['http://example.org/profile1']},
            'application/vnd.api+json; profile="http://example.org/profile1"',
        ),
        (
            {
                'ext': ['https://example.com/ext1', 'https://example.com/ext2'],
                'profile': ['http://example.org/profile1'],
            },
            'application/vnd.api+json; ext="https://example.com/ext1 https://example.com/ext2"; profile="http://example.org/profile1"',
        ),
        (
            {
                'profile': ['http://example.org/profile1', 'http://example.org/profile2'],
                'ext': ['https://example.com/ext1'],
            },
            'application/vnd.api+json; ext="https://example.com/ext1"; profile="http://example.org/profile1 http://example.org/profile2"',
        ),
    ],
)
def test_to_string(params, expected_str):
    ct = ContentType(media_type=ContentType.MEDIA_TYPE, params=params)
    assert ct.to_string() == expected_str


# Test Create Class Method


@pytest.mark.parametrize(
    'extensions, profiles, expected_params',
    [
        (None, None, {}),
        ([VALID_URI_1], None, {'ext': [VALID_URI_1]}),
        (None, [VALID_URI_2], {'profile': [VALID_URI_2]}),
        ([VALID_URI_1, VALID_URI_3], [VALID_URI_2], {'ext': [VALID_URI_1, VALID_URI_3], 'profile': [VALID_URI_2]}),
    ],
)
def test_create_method_valid(extensions, profiles, expected_params):
    ct = ContentType.create(extensions=extensions, profiles=profiles)
    assert ct.media_type == ContentType.MEDIA_TYPE
    assert ct.params == expected_params


@pytest.mark.parametrize(
    'extensions, profiles, error_message',
    [
        (['invalid_uri'], None, "Invalid URI in 'extensions': 'invalid_uri'"),
        (None, ['ftp://'], "Invalid URI in 'profiles': 'ftp://'"),
        (['https://valid.com', 'invalid_uri'], ['http://profile.com'], "Invalid URI in 'extensions': 'invalid_uri'"),
        (
            ['https://valid.com'],
            ['http://profile.com', 'invalid_profile_uri'],
            "Invalid URI in 'profiles': 'invalid_profile_uri'",
        ),
    ],
)
def test_create_method_invalid(extensions, profiles, error_message):
    with pytest.raises(ContentTypeError) as exc_info:
        ContentType.create(extensions=extensions, profiles=profiles)
    assert str(exc_info.value) == error_message


# Test _is_valid_uri Static Method


@pytest.mark.parametrize(
    'uri, expected',
    [
        (VALID_URI_1, True),
        (VALID_URI_2, True),
        (VALID_URI_3, True),
        (INVALID_URI_1, False),
        (INVALID_URI_2, False),
        ('https://', False),
        ('', False),
        ('justastring', False),
        ('http:///path', False),
    ],
)
def test_is_valid_uri(uri, expected):
    assert ContentType._is_valid_uri(uri) == expected


# Test Edge Cases


def test_parse_with_extra_spaces_and_order():
    content_type_str = (
        '  application/vnd.api+json ; profile="http://example.org/profile1" ; ext="https://example.com/ext1"  '
    )
    ct = ContentType.parse(content_type_str)
    assert ct.media_type == 'application/vnd.api+json'
    assert ct.params == {'profile': ['http://example.org/profile1'], 'ext': ['https://example.com/ext1']}


def test_to_string_sorted_parameters():
    params = {'profile': ['http://example.org/profile1'], 'ext': ['https://example.com/ext1']}
    ct = ContentType(media_type=ContentType.MEDIA_TYPE, params=params)
    expected_str = 'application/vnd.api+json; ext="https://example.com/ext1"; profile="http://example.org/profile1"'
    assert ct.to_string() == expected_str


def test_empty_parameters():
    content_type_str = 'application/vnd.api+json; ext'
    with pytest.raises(ContentTypeError) as exc_info:
        ContentType.parse(content_type_str)
    assert str(exc_info.value) == "Invalid parameter format: 'ext'"


def test_parameters_with_empty_quotes():
    content_type_str = 'application/vnd.api+json; ext=""'
    ct = ContentType.parse(content_type_str)
    assert ct.media_type == 'application/vnd.api+json'
    assert ct.params == {'ext': []}

    # Depending on specification, you might want to treat empty URIs as invalid
    # If so, adjust the test accordingly:
    # with pytest.raises(ContentTypeError) as exc_info:
    #     ContentType.parse(content_type_str)
    # assert str(exc_info.value) == "Invalid URI in 'ext': ''"


def test_content_type_success():
    # Test valid content type
    content_type_str = 'application/vnd.api+json; ext="https://example.com/extensions/feature"; profile="https://example.com/profiles/resource-timestamps https://example.com/profiles/another-profile"'
    content_type = ContentType.parse(content_type_str)
    assert content_type.media_type == 'application/vnd.api+json'
    assert content_type.params == {
        'ext': ['https://example.com/extensions/feature'],
        'profile': ['https://example.com/profiles/resource-timestamps', 'https://example.com/profiles/another-profile'],
    }


def test_content_invalid_media_type():
    # Test invalid media type
    content_type_str = 'application/json; ext="https://example.com/extensions/feature"; profile="https://example.com/profiles/resource-timestamps https://example.com/profiles/another-profile"'
    try:
        ContentType.parse(content_type_str)
    except ContentTypeError as e:
        assert str(e) == "Invalid media type 'application/json'. Expected 'application/vnd.api+json'."


def test_content_invalid_parameters():
    # Test invalid parameter
    content_type_str = (
        'application/vnd.api+json; ext="https://example.com/extensions/feature"; invalid="profile1 profile2"'
    )
    try:
        ContentType.parse(content_type_str)
    except ContentTypeError as e:
        assert str(e) == "Invalid parameter 'invalid'. Only 'ext' and 'profile' are allowed.", 'Invalid parameter'

    # Test invalid URI
    content_type_str = 'application/vnd.api+json; ext="https://example.com/extensions/feature"; profile="invalid"'
    try:
        ContentType.parse(content_type_str)
    except ContentTypeError as e:
        assert str(e) == "Invalid URI in 'profile': 'invalid'"

    # Test invalid parameter format
    content_type_str = 'application/vnd.api+json; ext="https://example.com/extensions/feature"; profile'
    try:
        ContentType.parse(content_type_str)
    except ContentTypeError as e:
        assert str(e) == "Invalid parameter format: 'profile'"


def test_content_type_construction():
    try:
        content_type = ContentType.create(
            extensions=['https://example.com/extensions/feature'],
            profiles=[
                'https://example.com/profiles/resource-timestamps',
                'https://example.com/profiles/another-profile',
            ],
        )
        content_type_str = content_type.to_string()
    except ContentTypeError as e:
        assert False, 'Unexpected ContentTypeError: ' + str(e)

    expected = 'application/vnd.api+json; ext="https://example.com/extensions/feature"; profile="https://example.com/profiles/resource-timestamps https://example.com/profiles/another-profile"'
    assert content_type_str == expected, 'Unexpected content type string: ' + content_type_str
