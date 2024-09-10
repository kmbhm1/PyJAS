import json
from typing import Any

from pyjas.core.util import is_valid_member_name, is_valid_url


class JsonAPISpecificationObject:
    """A class that provides methods to convert the object to a JSON string and vice versa."""

    def to_json(self) -> str:
        """Converts the object to a JSON string."""
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        """Converts the object to a dictionary."""
        return self.__dict__

    @classmethod
    def from_json(cls, data: str) -> 'JsonAPISpecificationObject':
        """Converts a JSON string to an object."""
        return cls(**json.loads(data))

    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        return f'{self.__class__.__name__}({self.to_dict()})'


class URL:
    """A custom URL type that validates the URL format upon initialization."""

    def __init__(self, url: str):
        if not is_valid_url(url):
            raise ValueError(f'Invalid URL: {url}')
        self._url = url

    def __str__(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return f'URL({self._url})'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, URL):
            return self._url == other._url
        return False

    def __hash__(self) -> int:
        return hash(self._url)


class MemberName:
    """A custom member name type that validates the format upon initialization."""

    def __init__(self, name: str):
        if not is_valid_member_name(name):
            raise ValueError(f'Invalid member name: {name}')
        self._name = name

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f'MemberName({self._name})'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MemberName):
            return self._name == other._name
        return False

    def __hash__(self) -> int:
        return hash(self._name)

    @staticmethod
    def is_valid_member_name(value: str) -> bool:
        """Checks if the given value matches the member name pattern.

        Args:
            value (str): The member name to validate.

        Returns:
            bool: True if the value matches the pattern, False otherwise.
        """
        return is_valid_member_name(value)
