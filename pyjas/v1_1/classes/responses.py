from typing import Any

from pyjas.core.classes import JsonAPISpecificationObject


class JsonAPIResponse(JsonAPISpecificationObject):
    """A class that represents a JSON API response."""

    def __init__(self, data: dict[str, Any], meta: dict[str, Any] = None, links: dict[str, Any] = None):
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

    def __init__(self):
        self._data = None
        self._errors = None
        self._meta = None
        self._links = None

    def data(self, data: dict[str, Any]) -> 'JsonAPIResponseBuilder':
        """Sets the data attribute."""
        self._data = data
        return self

    def meta(self, meta: dict[str, Any]) -> 'JsonAPIResponseBuilder':
        """Sets the meta attribute."""
        self._meta = meta
        return self

    def links(self, links: dict[str, Any]) -> 'JsonAPIResponseBuilder':
        """Sets the links attribute."""
        self._links = links
        return self

    def build(self) -> JsonAPIResponse:
        """Builds a JsonAPIResponse object."""
        return JsonAPIResponse(data=self._data, meta=self._meta, links=self._links)
