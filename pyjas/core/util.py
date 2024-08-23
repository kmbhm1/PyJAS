import re

# Regular expression to match valid URLs
url_regex = re.compile(
    r'^(https?://)'  # http:// or https://
    r'([a-zA-Z0-9-._~:/?#@!$&\'()*+,;=%]+)'  # Domain and path
    r'(\.[a-zA-Z]{2,6})'  # TLD (e.g., .com, .org)
    r'(:\d+)?'  # Optional port
    r'(/[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?$'  # Optional path and query parameters
)


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
