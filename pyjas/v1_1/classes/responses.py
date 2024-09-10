from typing import Any

from pyjas.core.classes import JsonAPISpecificationObject


class JsonAPIResponse(JsonAPISpecificationObject):
    """A class that represents a JSON API response."""

    def __init__(self, data: dict[str, Any], meta: dict[str, Any] | None = None, links: dict[str, Any] | None = None):
        self.data = data
        self.meta = meta
        self.links = links

    def _validate(self) -> None:
        pass

    @classmethod
    def builder(cls) -> 'JsonAPIResponseBuilder':
        """Returns a new instance of JsonAPIResponseBuilder."""
        return JsonAPIResponseBuilder()


class JsonAPIResponseBuilder:
    """A class that provides methods to build a JsonAPIResponse object."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._errors: list[Any] = []
        self._meta: dict[str, Any] = {}
        self._links: dict[str, Any] = {}

    @property
    def data(self) -> dict[str, Any]:
        """dict[str, Any]: Gets the data attribute."""
        return self._data

    @data.setter
    def data(self, data: dict[str, Any]) -> None:
        """Sets the data attribute."""
        self._data = data

    @property
    def errors(self) -> list[Any]:
        """list[Any]: Gets the errors attribute."""
        return self._errors

    @errors.setter
    def errors(self, errors: list[Any]) -> None:
        """Sets the errors attribute."""
        self._errors = errors

    @property
    def meta(self) -> dict[str, Any]:
        """dict[str, Any]: Gets the meta attribute."""
        return self._meta

    @meta.setter
    def meta(self, meta: dict[str, Any]) -> None:
        """Sets the meta attribute."""
        self._meta = meta

    @property
    def links(self) -> dict[str, Any]:
        """dict[str, Any]: Gets the links attribute."""
        return self._links

    @links.setter
    def links(self, links: dict[str, Any]) -> None:
        """Sets the links attribute."""
        self._links = links
