from pyjas.core.classes import MemberName
from pyjas.core.exceptions import PyJASException
from pyjas.core.util import is_valid_member_name


class JsonAPIResourceIdentifierObject:
    """A class to represent a JSON API resource identifier object.

    Args:
        type_ (str): ("type") The type of the resource.
        id_ (str): ("id") The unique identifier for the resource.
    """

    def __init__(
        self,
        type_: str | MemberName,
        id_: str,
        lid_: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        # Required attributes
        self.type_ = type_
        self.id_ = id_
        self.lid_ = lid_

        # Optional attributes
        self.meta = meta

        self._validate()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JsonAPIResourceIdentifierObject):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def _validate(self) -> None:
        if not self.type_:
            raise PyJASException('The type_ attribute must be set.')
        if bool(self.id_) == bool(self.lid_):
            raise PyJASException('Either the id_ or lid_ attribute must be set, but not both.')
        if isinstance(self.type_, str) and not is_valid_member_name(self.type_):
            raise PyJASException('The type_ attribute must be a valid member name.')

    def to_dict(self) -> dict[str, str]:
        """Returns the resource identifier object as a dictionary."""
        self._validate()

        d = {
            'type': self.type_,
            'id': self.id_,
            'lid': self.lid_,
            'meta': self.meta,
        }

        return {k: v for k, v in d.items() if v is not None}

    def builder(cls, type_: str, id_: str) -> 'JsonAPIResourceIdentifierObjectBuilder':
        """Returns a new instance of JsonAPIResourceIdentifierObjectBuilder."""
        return JsonAPIResourceIdentifierObjectBuilder(type_, id_)


class JsonAPIResourceIdentifierObjectBuilder:
    """A class to build a JSON API resource identifier object."""

    def __init__(self, type_: str | None = None, id_: str | None = None) -> None:
        self._resource_type = type_
        self._resource_id = id_

    @property
    def type_(self) -> str | None:
        """str | None: Gets the type of the resource."""
        return self._resource_type

    @type_.setter
    def set_type_(self, value: str | MemberName) -> None:
        """Sets the type of the resource."""
        if isinstance(self.type_, str) and not is_valid_member_name(value):
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

    def build(self) -> JsonAPIResourceIdentifierObject:
        """Builds the JSON API resource identifier object."""
        return JsonAPIResourceIdentifierObject(self.type_, self.id_)


JsonAPIResourceLinkageType = JsonAPIResourceIdentifierObject | list[JsonAPIResourceIdentifierObject] | None
