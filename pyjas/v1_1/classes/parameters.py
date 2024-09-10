from abc import ABCMeta, abstractmethod
from typing import Any

from pyjas.core.classes import JsonAPISpecificationObject
from pyjas.core.exceptions import PyJASException
from pyjas.core.util import transform_header_parameters, validate_extension_name, validate_uri_parameter

# Standard JSON API header
STANDARD_HEADER = 'application/vnd.api+json'


class JsaonAPIParameterRule(metaclass=ABCMeta):
    """A class that represents a JSON API parameter rule.

    This class is an abstract class that should apply to profiles or extensions.

    Args:
        name (str): The name of the rule.

    Example:
    >>> # Example implmentation of a JSON API parameter rule
    >>> class MyJsonRule(JsaonAPIParameterRule):
    ...    def evaluate(self, obj: Any) -> None:
    ...        # Implement your evaluation logic here
    ...        if not isinstance(obj, dict):
    ...            raise ValueError(f"Object is not a valid JSON document: {obj}")
    ...        # Add more rule checks here
    ...        print(f"Rule '{self.name}' passed for object: {obj}")
    """

    def __init__(self, name: str):
        self.name = name

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Allows the object to be called as a function."""
        return self.evaluate(*args, **kwds)

    @abstractmethod
    def evaluate(self, obj: Any) -> None:  # TODO: add JSONAPI Request type
        """Evaluates the extension rule against an object and raises an exception if the rule is violated."""
        raise NotImplementedError('This method is a future feature.')


class JsonAPIParameter(JsonAPISpecificationObject):
    """A class that represents a JSON API parameter.

    This can be an extension or profile.

    Args:
        uri (str): The URI of the profile.
        namespace (dict): The namespace of the profile. Contains the profile's members and data types. (e.g., 'atomic:operations': 'list[str]')
        description: The description of the profile.
    """  # noqa: E501

    def __init__(self, uri: str, rules: dict[str, JsaonAPIParameterRule], description: str | None = None):
        self.uri = uri
        assert self.uri is not None, 'The URI of the profile must be provided.'
        validate_uri_parameter(self.uri)

        self.description = description
        self.rules = rules

    def __eq__(self, o: Any) -> bool:
        """Compares two objects."""
        if not isinstance(o, JsonAPIProfile):
            return False
        return self.uri == o.uri

    def evaluate(self, request: Any) -> bool:  # TODO: add JSONAPI Request type
        """Evaluates the extension against a request."""
        for rule in self.rules.values():
            rule(request)  # Evaluate the request
        return True  # TODO: correct this; placeholder

    def value(self) -> str:
        """Converts the object to a string."""
        return transform_header_parameters(self.uri)


class JsonAPIExtension(JsonAPIParameter):
    """A class that represents a JSON API extension.

    Extension Rules:
        - Extensions provide a means to “extend” the base specification by defining additional specification semantics.
        - Extensions cannot alter or remove specification semantics, nor can they specify implementation semantics.
        - An extension MAY impose additional processing rules or further restrictions and it MAY define new object members as described below.
        - An extension MUST NOT lessen or remove any processing rules, restrictions or object member requirements defined in this specification or other extensions.
        - An extension MAY define new members within the document structure defined by this specification. The rules for extension member names are covered below.
        - An extension MAY define new query parameters. The rules for extension-defined query parameters are covered below.

    Args:
        uri (str): The URI of the extension.
        namespace (dict): The namespace of the extension. Contains the extension's members and data types. (e.g., 'atomic:operations': 'list[str]')
        description: The description of the extension.
        rules: The rules for evaluating the extension. This should be a Callable function that evaluates a top-level document.
    """  # noqa: E501

    def __init__(
        self,
        uri: str,
        namespace: dict[str, Any],
        rules: dict[str, JsaonAPIParameterRule],
        description: str | None = None,
    ):
        super().__init__(uri, rules, description)

        self.namespace = namespace

        # Validate the parameters
        self._validate()

    def _validate(self) -> None:
        """Validate the parameters."""
        assert self.namespace is not None, 'The namespace of the extension must be provided.'

        for key in self.namespace.keys():
            if not validate_extension_name(key):
                raise PyJASException(f'Invalid extension extension: {key}')


class JsonAPIProfile(JsonAPIParameter):
    """A class that represents a JSON API profile.

    Unlike extensions, profiles do not need to define a namespace for document members because profiles cannot
    define specification semantics and thus cannot conflict with current or future versions of this specification.
    However, it is possible for profiles to conflict with other profiles. Therefore, it is the responsibility
    of implementors to ensure that they do not support conflicting profiles.

    Profile Rules:
    - A profile MAY define document members and processing rules that are reserved for implementors.
    - A profile MUST NOT define any query parameters except implementation-specific query parameters.
    - A profile MUST NOT alter or remove processing rules that have been defined by this specification or by an extension. However, a profile MAY define processing rules for query parameters whose processing rules have been reserved for implementors to define at their discretion.

    Args:
        uri (str): The URI of the profile.
        namespace (dict): The namespace of the profile. Contains the profile's members and data types. (e.g., 'atomic:operations': 'list[str]')
        description: The description of the profile.
    """  # noqa: E501


class JsonAPIHeader(JsonAPISpecificationObject):
    """A class that represents a JSON API Specification header.

    ## Extension Rules:

    - Extensions provide a means to “extend” the base specification by defining additional specification semantics.
    - Extensions cannot alter or remove specification semantics, nor can they specify implementation semantics.
    - An extension MAY impose additional processing rules or further restrictions and it MAY define new object members as described below.
    - An extension MUST NOT lessen or remove any processing rules, restrictions or object member requirements defined in this specification or other extensions.
    - An extension MAY define new members within the document structure defined by this specification. The rules for extension member names are covered below.
    - An extension MAY define new query parameters. The rules for extension-defined query parameters are covered below.

    ## Profile Rules:

    - Profiles provide a means to share a particular usage of the specification among implementations.
    - Profiles can specify implementation semantics, but cannot alter, add to, or remove specification semantics.

    Args:
        ext (JsonAPIExtension | list[JsonAPIExtension]): The extension(s) to include in the header.
        profile (str | list[str]): The profile(s) to include in the header.
    """  # noqa: E501

    def __init__(
        self, ext: JsonAPIExtension | list[JsonAPIExtension] | None = None, profile: str | list[str] | None = None
    ):
        self.ext = ext
        self.profile = profile
        self._content_type = STANDARD_HEADER

        # Validate the parameters
        self._validate()

    def _validate(self) -> None:
        """Validate the parameters."""
        if self.ext is not None:
            uris = [e.uri for e in self.ext] if isinstance(self.ext, list) else [self.ext.uri]
            validate_uri_parameter(uris)
        if self.profile is not None:
            validate_uri_parameter(self.profile)

    def content_type(self) -> dict[str, Any]:
        """Converts the object to a dictionary."""
        header = self._content_type
        if self.ext:
            items = [e.value() for e in self.ext] if isinstance(self.ext, list) else [self.ext.value()]
            header += f'; ext={transform_header_parameters(items)}'
        if self.profile:
            header += f'; profile={transform_header_parameters(self.profile)}'

        return {'Content-Type': header}

    def accept(self) -> dict[str, Any]:
        """Converts the object to a dictionary."""
        header = self._content_type
        if self.ext:
            items = [e.value() for e in self.ext] if isinstance(self.ext, list) else [self.ext.value()]
            header += f'; ext={transform_header_parameters(items)}'
        if self.profile:
            header += f'; profile={transform_header_parameters(self.profile)}'

        return {'Accept': header}

    @classmethod
    def builder(cls) -> 'JsonAPIHeaderBuilder':
        """Returns a new instance of JsonAPIHeaderBuilder."""
        return JsonAPIHeaderBuilder()


class JsonAPIHeaderBuilder:
    """A class that provides methods to build a JsonAPIHeader object."""

    def __init__(self) -> None:
        self._ext: list[JsonAPIExtension] = []
        self._profile: list[str] = []

    def from_string(self, header: str) -> 'JsonAPIHeaderBuilder':
        """Sets the header from a string."""
        if header:
            parts = header.split(';')
            self._content_type = parts[0]
            for part in parts[1:]:
                key, value = part.split('=')
                if key == 'ext':
                    # TODO: Correct this later
                    ext = JsonAPIExtension(value, {}, {})
                    self._ext.append(ext)
                elif key == 'profile':
                    self._profile.append(value)
                else:
                    raise ValueError(f'Unsupported Media Type: {key}')
        return self

    def add_ext(self, ext: JsonAPIExtension) -> 'JsonAPIHeaderBuilder':
        """Sets the ext attribute."""
        self._ext.append(ext)
        return self

    def remove_ext(self, ext: JsonAPIExtension) -> 'JsonAPIHeaderBuilder':
        """Removes an ext attribute."""
        self._ext.remove(ext)
        return self

    def clear_ext(self) -> 'JsonAPIHeaderBuilder':
        """Clears the ext attribute."""
        self._ext = []
        return self

    def add_profile(self, profile: str) -> 'JsonAPIHeaderBuilder':
        """Sets the profile attribute."""
        self._profile.append(profile)
        return self

    def remove_profile(self, profile: str) -> 'JsonAPIHeaderBuilder':
        """Removes a profile attribute."""
        self._profile.remove(profile)
        return self

    def clear_profile(self) -> 'JsonAPIHeaderBuilder':
        """Clears the profile attribute."""
        self._profile = []
        return self

    def build(self) -> JsonAPIHeader:
        """Builds a JsonAPIHeader object."""
        return JsonAPIHeader(ext=self._ext, profile=self._profile)
