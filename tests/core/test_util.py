from pyjas.core.util import is_valid_url, transform_header_parameters


def test_is_valid_url():
    assert is_valid_url('https://example.com') is True
    assert is_valid_url('http://example.com') is True
    assert is_valid_url('https://example.com:8080') is True
    assert is_valid_url('https://example.com/path/to/resource') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?/') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?/!') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?/!@') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?/!@#') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?/!@#*') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?/!@#*(') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?/!@#*()') is True
    assert is_valid_url('https://example.com/path/to/resource?query=param&another=param#fragment?#?/!@#*()=') is True
    assert is_valid_url('https://example.com') is True
    assert is_valid_url('http://example.com/path/to/resource?query=param#fragment') is True
    assert is_valid_url('ftp://invalid-protocol.com') is False
    assert is_valid_url('https://another-example.org:8080/path') is True
    assert is_valid_url('invalid-url') is False


def test_transform_header_parameters():
    assert transform_header_parameters('value') == '"value"'
    assert transform_header_parameters(['value1', 'value2']) == '"value1", "value2"'
    assert transform_header_parameters(None) == ''
    assert transform_header_parameters('') == ''
    assert transform_header_parameters([]) == ''
    assert transform_header_parameters(['']) == ''
    assert transform_header_parameters(['', '']) == ''
    assert transform_header_parameters(['val' for _ in range(4)]) == '"val", "val", "val", "val"'
