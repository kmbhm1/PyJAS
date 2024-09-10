from typing import Any

from pydantic import BaseModel

from pyjas.core.exceptions import PyJASException


class JsonAPIAttributesObject:
    """A class to represent a JSON API attributes object.

    Notes:
        - The value of the attributes key MUST be an object (an “attributes object”). Members of the attributes object (“attributes”) represent information about the resource object in which it's defined.
        - Attributes may contain any valid JSON value, including complex data structures involving JSON objects and arrays.
        - Keys that reference related resources (e.g. author_id) SHOULD NOT appear as attributes. Instead, relationships SHOULD be used.

    Args:
        o (BaseModel): The attributes of the resource. A Pydantic model.
    """  # noqa: E501

    def __init__(self, attributes: BaseModel | dict[str, Any]) -> None:
        self.attributes = attributes

        self._validate()

    def __call__(self) -> dict[str, Any]:
        """Returns the attributes as a dictionary."""
        return self.to_dict()

    def _validate(self) -> None:
        if not self.attributes:
            raise PyJASException('The attributes attribute must be set.')

    def to_dict(self) -> dict[str, Any]:
        """Returns the attributes as a dictionary."""
        if isinstance(self.attributes, BaseModel):
            return self.attributes.model_dump()
        return self.attributes

    @classmethod
    def builder(cls, o: BaseModel) -> 'JsonAPIAttributesBuilder':
        """Returns a new instance of JsonAPIAttributesBuilder."""
        return JsonAPIAttributesBuilder(o)


class JsonAPIAttributesBuilder:
    """A class to build a JSON API attributes object."""

    def __init__(self, o: BaseModel | None = None) -> None:
        self._attributes: dict[str, Any] = o.model_dump() if o else {}

    @property
    def attributes(self) -> dict[str, Any]:
        """BaseModel: Gets the attributes of the resource."""
        return self._attributes

    @attributes.setter
    def attributes(self, value: BaseModel | dict) -> None:
        """Sets the attributes of the resource."""
        if isinstance(value, dict):
            self._attributes = value
        else:
            self._attributes = value.model_dump()

    def build(self) -> JsonAPIAttributesObject:
        """Returns a new instance of JsonAPIAttributesObject."""
        return JsonAPIAttributesObject(self._attributes)
