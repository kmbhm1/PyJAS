from typing import Any

from pyjas.core.classes import JsonAPISpecificationObject
from pyjas.core.exceptions import PyJASException
from pyjas.core.util import validate_uri_parameter
from pyjas.v1_1.classes.jsonapi_implementation import JSONAPIImplementationObject
from pyjas.v1_1.classes.links import JsonAPITopLevelLinksObject
from pyjas.v1_1.classes.resources.resource import JsonAPIResourceObject
from pyjas.v1_1.classes.resources.resource_identifier import JsonAPIResourceIdentifierObject


class JsonAPIDocument(JsonAPISpecificationObject):
    """A class that represents a JSON API document.

    Attributes:
        data: The document's "primary data".
        errors: An array of error objects.
        meta: A meta object that contains non-standard meta-information.
        jsonapi: An object describing the server's implementation.
        links: A links object related to the primary data.
        included: An array of resource objects that are related to the primary data and/or each other. (i.e. the "included resources"s)
        kwargs: Additional, extension attributes.
    """  # noqa: E501

    def __init__(
        self,
        data: JsonAPIResourceObject
        | list[JsonAPIResourceObject]
        | JsonAPIResourceIdentifierObject
        | list[JsonAPIResourceIdentifierObject]
        | None = None,
        errors: list[Any] | None = None,
        meta: dict[str, Any] | None = None,
        jsonapi: JSONAPIImplementationObject | None = None,
        links: JsonAPITopLevelLinksObject | None = None,
        included: list[JsonAPIResourceObject] | None = None,
        **kwargs: Any,  # Accept arbitrary additional, extension attributes
    ):
        # Required attributes
        self.data = data
        self.errors = errors
        self.meta = meta
        self.extension_members = kwargs

        # Optional attributes
        self.jsonapi = jsonapi
        self.links = links
        self.included = included

        # Validate the object
        self._validate()

    def _validate(self) -> None:
        if all([x is None for x in (self.data, self.errors, self.meta, self.extension_members)]):
            raise PyJASException(
                'At least one of the top-level members data, errors, meta, or extension attributes must be set.'
            )
        if bool(self.data) == bool(self.errors):
            raise PyJASException(
                'At least one of the data or errors attributes must be set, but not both, in the same document.'
            )
        if not bool(self.data) and bool(self.included):
            raise PyJASException(
                'The included attribute cannot be set if the document does not contain a top-level data member.'
            )
        if self.links is not None and isinstance(self.links, str):
            try:
                validate_uri_parameter(self.links)
            except ValueError:
                raise PyJASException('The links attribute must be a valid URL.')

    def add_extension_member(self, name: str, value: Any) -> None:
        """Dynamically adds an attribute to the instance if the value is not None."""
        if value is not None:
            setattr(self, name, value)
            self.extension_members[name] = value  # Store in additional attributes
            self._validate()  # Re-validate after adding the attribute

    def to_dict(self) -> dict[str, Any]:
        """Returns the document as a dictionary."""
        self._validate()

        data = (
            ([x.to_dict() for x in self.data] if isinstance(self.data, list) else self.data.to_dict())
            if self.data
            else None
        )
        d = {
            'data': data,
            'errors': self.errors if self.errors else None,
            'meta': self.meta if self.meta else None,
            **self.extension_members,  # Include additional attributes
            'included': [i.to_dict() for i in self.included] if self.included else None,
            'links': self.links.to_dict() if self.links else None,
            'jsonapi': self.jsonapi if self.jsonapi else None,
        }

        return {k: v for k, v in d.items() if v is not None}

    @classmethod
    def builder(cls) -> 'JsonAPIDocumentBuilder':
        """Returns a new instance of JsonAPIDocumentBuilder."""
        return JsonAPIDocumentBuilder()


class JsonAPIDocumentBuilder:
    """A class to build a JSON API document."""

    def __init__(self) -> None:
        self._data: (
            JsonAPIResourceObject
            | list[JsonAPIResourceObject]
            | JsonAPIResourceIdentifierObject
            | list[JsonAPIResourceIdentifierObject]
            | None
        ) = None
        self._errors: list[Any] = []
        self._meta: dict[str, Any] = {}
        self._jsonapi: JSONAPIImplementationObject | None = None
        self._links: JsonAPITopLevelLinksObject = JsonAPITopLevelLinksObject()
        self._included: list[JsonAPIResourceObject] = []
        self._extension_members: dict[str, Any] = {}

    @property
    def data(
        self,
    ) -> (
        JsonAPIResourceObject
        | list[JsonAPIResourceObject]
        | JsonAPIResourceIdentifierObject
        | list[JsonAPIResourceIdentifierObject]
        | None
    ):
        """JsonAPIResourceObject | list[JsonAPIResourceObject] | JsonAPIResourceIdentifierObject | list[JsonAPIResourceIdentifierObject] | None: Gets the document's primary data."""  # noqa: E501
        return self._data

    @data.setter
    def data(
        self,
        value: JsonAPIResourceObject
        | list[JsonAPIResourceObject]
        | JsonAPIResourceIdentifierObject
        | list[JsonAPIResourceIdentifierObject]
        | None,
    ) -> None:
        """Sets the document's primary data."""
        self._data = value

    @property
    def errors(self) -> list[Any]:
        """list[Any]: Gets the document's error objects."""
        return self._errors

    @errors.setter
    def errors(self, value: list[Any]) -> None:
        """Sets the document's error objects."""
        self._errors = value

    @property
    def meta(self) -> dict[str, Any]:
        """dict[str, Any]: Gets the document's meta object."""
        return self._meta

    @meta.setter
    def meta(self, value: dict[str, Any]) -> None:
        """Sets the document's meta object."""
        self._meta = value

    @property
    def jsonapi(self) -> JSONAPIImplementationObject | None:
        """str: Gets the document's JSON API object."""
        return self._jsonapi

    @jsonapi.setter
    def jsonapi(self, value: JSONAPIImplementationObject) -> None:
        """Sets the document's JSON API object."""
        self._jsonapi = value

    @property
    def links(self) -> JsonAPITopLevelLinksObject:
        """JsonAPILinksType: Gets the document's links object."""
        return self._links

    @links.setter
    def links(self, value: JsonAPITopLevelLinksObject) -> None:
        """Sets the document's links object."""
        self._links = value

    @property
    def included(self) -> list[JsonAPIResourceObject]:
        """list[JsonAPIResourceObject]: Gets the document's included resources."""
        return self._included

    @included.setter
    def included(self, value: list[JsonAPIResourceObject] | JsonAPIResourceObject) -> None:
        """Sets the document's included resources."""
        if isinstance(value, list):
            self._included = value
        elif value is not None:
            self._included = [value]

    @property
    def extension_members(self) -> dict[str, Any]:
        """dict[str, Any]: Gets the document's extension attributes."""
        return self._extension_members

    def add_extension_member(self, name: str, value: Any) -> 'JsonAPIDocumentBuilder':
        """Adds an extension attribute to the document."""
        self._extension_members[name] = value
        return self

    def build(self) -> JsonAPIDocument:
        """Builds the JSON API document."""
        if bool(self.data) == bool(self.errors):
            raise PyJASException(
                'At least one of the data or errors attributes must be set, but not both, in the same document.'
            )

        return JsonAPIDocument(
            data=self.data,
            errors=self.errors,
            meta=self.meta,
            jsonapi=self.jsonapi,
            links=self.links,
            included=self.included,
            **self.extension_members,  # Include additional attributes
        )
