# validate_member_name tests

# Define the reserved characters as per the validate_member_name function
from pyjas.v1_1.jsonapi_builder import validate_member_name
import pytest

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
