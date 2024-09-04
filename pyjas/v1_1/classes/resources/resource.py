from typing import Any

from deepdiff import DeepDiff

from pyjas.core.classes import MemberName
from pyjas.core.exceptions import PyJASException
from pyjas.core.util import is_valid_member_name
from pyjas.v1_1.classes.links import JsonAPITopLevelLinksObject
from pyjas.v1_1.classes.resources.attribute import JsonAPIAttributesObject
from pyjas.v1_1.classes.resources.relationship import JsonAPIRelationshipsObject


class JsonAPIResourceObject:
    """A class to represent a JSON API resource object.

    Args:
        type_ (str): ("type") The type of the resource.
        attributes (JsonAPIAttributesObject): The attributes of the resource.
        relationships (JsonAPIRelationshipsObject): The relationships of the resource.
        id_ (str): ("id") The unique identifier for the resource.
        lid_ (str): ("lid") The local identifier for the resource.
    """

    def __init__(
        self,
        type_: str | MemberName,
        attributes: JsonAPIAttributesObject,
        relationships: dict[str, JsonAPIRelationshipsObject],
        id_: str | None = None,
        lid_: str | None = None,
        links: JsonAPITopLevelLinksObject | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        # Required attributes
        self.type_ = type_
        self.id_ = id_
        self.lid_ = lid_

        # Optional attributes
        self.attributes = attributes
        self.relationships = relationships
        self.links = links
        self.meta = meta

        self._validate()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JsonAPIResourceObject):
            return False

        diff = self.compare(other)

        return not bool(diff)

    def compare_to(self, other: 'JsonAPIResourceObject') -> dict[str, Any]:
        """Compares the resource object to another resource object and returns the differences."""
        return DeepDiff(self.to_dict(), other.to_dict()).to_dict()

    def compare_by_required(self, other: 'JsonAPIResourceObject') -> bool:
        """Compares the resource object to another resource object by required attributes."""
        id_comparison = False

        if self.id_ is not None:
            id_comparison = self.id_ == other.id_
        elif self.lid_ is not None:
            id_comparison = self.lid_ == other.lid_
        else:
            raise PyJASException('The id or lid attribute must be set in both objects.')

        return self.type_ == other.type_ and id_comparison

    def _validate(self) -> None:
        if not self.type_:
            raise PyJASException('The resource type must be set.')
        if bool(self.id_) == bool(self.lid_):
            raise PyJASException('Either the id or lid attribute must be set, but not both.')
        if isinstance(self.type_, str) and not is_valid_member_name(self.type_):
            raise PyJASException('The type_ attribute must be a valid member name.')
        # TODO: add validation for note: https://jsonapi.org/format/#document-resource-object-attributes
        # about attributes not containing references to related resources

    def to_dict(self) -> dict[str, Any]:
        """Returns the resource object as a dictionary."""
        # Validate the object first
        self._validate()

        required = ['type', 'attributes', 'relationships']
        d = {
            'type': self.type_,
            'id': self.id_ if (self.id_ and not self.lid_) else None,
            'lid': self.lid_ if (not self.id_ and self.lid_) else None,
            'attributes': self.attributes.attributes,
            'relationships': self.relationships.relationships,
        }

        d = {k: v for k, v in d.items() if v is not None or k in required}

        return d

    @classmethod
    def builder(cls, type_: str) -> 'JsonAPIResourceObjectBuilder':
        """Returns a new instance of the JsonAPIResourceObjectBuilder class."""
        return JsonAPIResourceObjectBuilder(type_)


class JsonAPIResourceObjectBuilder:
    """A class to build a JSON API resource object.

    Args:
        type_ (str): ("type") The type of the resource.
    """

    def __init__(self, type_: str | None = None) -> None:
        self._resource_type = type_
        self._resource_id = None
        self._resource_local_id = None
        self._attributes = None
        self._relationships = None

    @property
    def type_(self) -> str | None:
        """str | None: Gets the type of the resource."""
        return self._resource_type

    @type_.setter
    def set_type_(self, value: str | MemberName) -> None:
        """Sets the type of the resource."""
        if isinstance(self.type_, str) and not is_valid_member_name(self.type_):
            raise PyJASException('The type_ attribute must be a valid member name.')
        self._resource_type = value

    @property
    def id_(self) -> str | None:
        """str | None: Gets the unique identifier for the resource."""
        return self._resource_id

    @id_.setter
    def set_id_(self, value: str) -> None:
        """Sets the unique identifier for the resource."""
        self._resource_id = value

    @property
    def lid_(self) -> str | None:
        """str | None: Gets the local identifier for the resource."""
        return self._resource_local_id

    @lid_.setter
    def set_lid_(self, value: str) -> None:
        """Sets the local identifier for the resource."""
        self._resource_local_id = value

    @property
    def attributes(self) -> JsonAPIAttributesObject | None:
        """JsonAPIAttributesObject | None: Gets the attributes of the resource."""
        return self._attributes

    @attributes.setter
    def set_attributes(self, value: JsonAPIAttributesObject) -> None:
        """Sets the attributes of the resource."""
        self._attributes = value

    @property
    def relationships(self) -> JsonAPIRelationshipsObject | None:
        """JsonAPIRelationshipsObject | None: Gets the relationships of the resource."""
        return self._relationships

    @relationships.setter
    def set_relationships(self, value: JsonAPIRelationshipsObject) -> None:
        """Sets the relationships of the resource."""
        self._relationships = value

    def build(self) -> JsonAPIResourceObject:
        """Builds and returns a new instance of the JsonAPIResourceObject class."""
        return JsonAPIResourceObject(
            type_=self.type_,
            id_=self.id_,
            lid_=self.lid_,
            attributes=self.attributes,
            relationships=self.relationships,
        )
