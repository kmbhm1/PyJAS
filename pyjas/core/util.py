import re

# Regular expression to match valid URLs
url_regex = re.compile(
    r'^(https?://)'  # http:// or https://
    r'([a-zA-Z0-9-._~:/?#@!$&\'()*+,;=%]+)'  # Domain and path
    r'(\.[a-zA-Z]{2,6})'  # TLD (e.g., .com, .org)
    r'(:\d+)?'  # Optional port
    r'(/[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?$'  # Optional path and query parameters
)


# Basic regex to match language tags according to RFC 5646
# ref: https://datatracker.ietf.org/doc/html/rfc5646
hreflang_regex = re.compile(
    r'^[a-zA-Z]{2,3}'  # Primary language (2-3 letters)
    r'(-[a-zA-Z]{4})?'  # Optional script (4 letters)
    r'(-[a-zA-Z]{2}|\d{3})?'  # Optional region (2 letters or 3 digits)
    r'(-[a-zA-Z0-9]{5,8})*'  # Optional variant (5-8 alphanumeric)
    r'(-[a-zA-Z0-9]{1,8})*$',  # Optional extensions (1-8 alphanumeric)
    re.IGNORECASE,
)

# Regex pattern to match namespaces that meet the specified criteria
# ref: https://jsonapi.org/format/#extension-rules
namespace_regex = re.compile(r'^[a-zA-Z0-9]+$')


# Regular expression to match document member names
# ref: https://jsonapi.org/format/#document-member-names
member_name_regex = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_ -]*[a-zA-Z0-9]$')

# Regular expression to match disallowed characters in member names
# ref: https://jsonapi.org/format/#document-member-names-reserved-characters
disallowed_member_name_regex = re.compile(r'[+,\.\[\]!"#$%&\'\(\)\*\/:;<=>\?\^`\{\|\}~\x7F\x00-\x1F\\]')


# Regular expression to ensure '@' can only be at the start of the string
# ref: https://jsonapi.org/format/#document-member-names-at-members
commercial_at_symbol_regex = re.compile(r'^@[^@]*$')


# Regex pattern to check if a colon is in the middle of the string and appears only once
colon_in_middle_once_regex = re.compile(r'^[^:]+:[^:]+$')


def is_valid_url(url: str) -> bool:
    """Checks if a URL is valid."""
    # Match the regex pattern to the input URL
    return re.match(url_regex, url) is not None


def validate_uri_parameter(parameter: str | list[str]) -> None:
    """Validates a URL parameter."""
    # If the parameter is a string, check if it is a valid URL
    if isinstance(parameter, str):
        if not is_valid_url(parameter):
            raise ValueError('ext must be a valid URL: ' + parameter)

    # If the parameter is a list, check if all elements are valid URLs
    if isinstance(parameter, list):
        for value in parameter:
            if not is_valid_url(value):
                raise ValueError('ext contains an invalid URL: ' + value)


def transform_header_parameters(parameters: str | list[str] | None) -> str:
    """Transforms a list of header parameters into a string."""
    # If the input is None, return an empty string
    if parameters is None or not bool(parameters):
        return ''

    # If the input is a string, return it
    if isinstance(parameters, str):
        return f'"{parameters}"'

    # Filter out empty strings
    parameters = [p for p in parameters if bool(p)]

    # If the input is a list, join the elements
    return ' '.join([f'"{p}"' for p in parameters]) if bool(parameters) else ''


def is_valid_hreflang(value: str) -> bool:
    """Checks if a string is a valid language tag."""
    return re.match(hreflang_regex, value) is not None


def member_name_has_valid_structure(name: str) -> bool:
    """Checks if a string has a valid structure for a member name."""
    return re.match(member_name_regex, name) is not None


def member_name_has_invalid_characters(name: str) -> bool:
    """Checks if a string has disallowed characters for a member name."""
    return re.search(disallowed_member_name_regex, name) is not None


def member_name_has_valid_commercial_at_symbol(name: str) -> bool:
    """Checks if a string has a valid commercial at symbol for a member name."""
    if '@' in name:
        return re.match(commercial_at_symbol_regex, name) is not None
    return True


def is_valid_member_name(name: str) -> bool:
    """Checks if a string is a valid member name."""
    return (
        member_name_has_valid_structure(name)
        and not member_name_has_invalid_characters(name)
        and member_name_has_valid_commercial_at_symbol(name)
    )


def is_valid_namespace(namespace: str) -> bool:
    """Checks if a string is a valid namespace."""
    return re.match(namespace_regex, namespace) is not None


def validate_extension_name(name: str) -> None:
    """Validates an extension name."""
    # Check that colon appears in string
    if ':' in name:
        # Check that colon appears only once and in the middle
        if not re.match(colon_in_middle_once_regex, name):
            return False
        else:
            # Split the string at the colon - namespace:extension
            namespace, member_name = name.split(':')

            # Check if the namespace is simple alphanumeric
            if not is_valid_namespace(namespace):
                return False

            # Check if the member name is valid
            if not is_valid_member_name(member_name):
                return False

            return True
    else:
        # Check namespace is simple alphanumeric
        return is_valid_namespace(name)
