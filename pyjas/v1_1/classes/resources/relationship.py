from typing import Any

from pyjas.core.exceptions import PyJASException
from pyjas.v1_1.classes.links import JsonAPITopLevelLinksObject
from pyjas.v1_1.classes.resources.resource_identifier import JsonAPIResourceLinkageType


class JsonAPIRelationshipsObject:
    """A class to represent a JSON API relationships object.

    Args:
        links (JsonAPITopLevelLinksObject | None): The links object for the relationships.
        data (JsonAPIResourceLinkageType | None): The data object for the relationships.
        meta (dict[str, Any] | None): Metadata for the relationships.
        **kwargs (Any): Additional attributes for the relationships.
    """

    def __init__(
        self,
        links: JsonAPITopLevelLinksObject | None = None,
        data: JsonAPIResourceLinkageType | None = None,
        meta: dict[str, Any] | None = None,
        **kwargs: Any,  # Accept arbitrary additional attributes
    ) -> None:
        self.links = links
        self.data = data
        self.meta = meta
        self.additional_members: dict[str, Any] = kwargs  # Store additional attributes

        self._validate()

    def _validate(self) -> None:
        # Validate required attributes
        if not self.links and not self.data and not self.meta and not self.additional_members:
            raise PyJASException('At least one of the links, data, meta, or additional attributes must be set.')

        # Validate links
        if self.links is not None:
            if self.links.self_ is None and self.links.related is None:
                raise PyJASException('At least one of the self or related attributes must be set.')

    def add_extension_member(self, name: str, value: Any) -> None:
        """Dynamically adds an attribute to the instance if the value is not None."""
        if value is not None:
            setattr(self, name, value)
            self.additional_members[name] = value  # Store in additional attributes
            self._validate()  # Re-validate after adding the attribute

    def to_dict(self) -> dict[str, Any]:
        """Returns the relationships object as a dictionary."""
        self._validate()

        data = (
            ([x.to_dict() for x in self.data] if isinstance(self.data, list) else self.data.to_dict())
            if self.data
            else None
        )
        relationships = {
            'links': self.links.to_dict() if self.links else None,
            'data': data,
            'meta': self.meta if self.meta else None,
            **self.additional_members,  # Include additional attributes
        }

        return {k: v for k, v in relationships.items() if v is not None}

    @classmethod
    def builder(cls) -> 'JsonAPIRelationshipsBuilder':
        """Returns a new instance of JsonAPIRelationshipsBuilder."""
        return JsonAPIRelationshipsBuilder()


class JsonAPIRelationshipsBuilder:
    """A class to build a JSON API relationships object."""

    def __init__(self) -> None:
        self._links: JsonAPITopLevelLinksObject | None = None
        self._data: JsonAPIResourceLinkageType | None = None
        self._meta: dict[str, Any] = {}
        self._additional_members: dict[str, Any] = {}  # Dictionary to hold arbitrary attributes

    @property
    def links(self) -> JsonAPITopLevelLinksObject | None:
        """JsonAPITopLevelLinksObject | None: Gets the links of the resource."""
        return self._links

    @links.setter
    def links(self, value: JsonAPITopLevelLinksObject | None) -> None:
        """Sets the links of the resource."""
        self._links = value

    @property
    def data(self) -> JsonAPIResourceLinkageType | None:
        """JsonAPIResourceLinkageType: Gets the data of the resource."""
        return self._data

    @data.setter
    def data(self, value: JsonAPIResourceLinkageType | None) -> None:
        """Sets the data of the resource."""
        self._data = value

    @property
    def meta(self) -> dict[str, Any]:
        """dict[str, Any]: Gets the meta of the resource."""
        return self._meta

    @meta.setter
    def meta(self, value: dict[str, Any]) -> None:
        """Sets the meta of the resource."""
        self._meta = value

    def add_extension_member(self, name: str, value: Any) -> 'JsonAPIRelationshipsBuilder':
        """Adds a dynamic extension attribute to the relationships object."""
        if value is not None:
            self._additional_members[name] = value
        return self  # Return self to allow method chaining

    def build(self) -> JsonAPIRelationshipsObject:
        """Returns a new instance of JsonAPIRelationshipsObject."""
        # Pass all attributes, including additional ones, to the constructor
        return JsonAPIRelationshipsObject(
            self.links,
            self.data,
            self.meta,
            **self._additional_members,  # Unpack the additional attributes
        )
