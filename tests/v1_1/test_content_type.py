from pyjas.v1_1.content_negotiation import ContentType, ContentTypeError


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
