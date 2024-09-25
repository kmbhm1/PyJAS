from __future__ import annotations

# jsonapi_document.py
import re
import uuid
from typing import Annotated, Any, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    conlist,
    constr,
    field_validator,
    model_validator,
)

from pyjas.v1_1.helper import is_valid_uri


def validate_member_name(name: str) -> None:
    """Validates a JSON:API member name according to the specification rules.

    Refer to https://jsonapi.org/format/#document-member-names for more information.

    Args:
        name (str): The member name to validate.

    Raises:
        ValueError: If the member name does not comply with the rules.
    """
    if not isinstance(name, str):
        raise ValueError('Member name must be a string.')

    if len(name) == 0:
        raise ValueError('Member name must contain at least one character.')

    # Reserved characters (must not be present)
    reserved_characters = set(
        '+,.,[,],!,",#,,$,%,&,\',(,),*,/,:,;,<,=,>,?,\\,^,`,{,|,},~,DEL'
    )  # 'DEL' represents U+007F
    # Note: 'DEL' is non-printable; in practice, it's handled by character ranges.

    # Define allowed characters using regex
    # Globally allowed: a-z, A-Z, 0-9, and U+0080+
    # Internal allowed: -, _, space
    # Extension members start with namespace followed by colon

    # Regex patterns
    # Pattern for the core allowed characters (excluding @-Members and extension members)
    core_pattern = r'^[A-Za-z0-9\u0080-\uFFFF](?:[A-Za-z0-9\u0080-\uFFFF\-_\ ]*[A-Za-z0-9\u0080-\uFFFF])?$'

    # Pattern for @-Members
    at_member_pattern = r'^@[A-Za-z0-9\u0080-\uFFFF](?:[A-Za-z0-9\u0080-\uFFFF\-_\ ]*[A-Za-z0-9\u0080-\uFFFF])?$'

    # Pattern for Extension Members (namespace:member)
    extension_pattern = r'^[A-Za-z0-9\u0080-\uFFFF]+:[A-Za-z0-9\u0080-\uFFFF](?:[A-Za-z0-9\u0080-\uFFFF\-_\ ]*[A-Za-z0-9\u0080-\uFFFF])?$'  # noqa: E501

    if re.match(core_pattern, name):
        pass  # Valid core member name
    elif re.match(at_member_pattern, name):
        pass  # Valid @-Member
    elif re.match(extension_pattern, name):
        pass  # Valid Extension Member
    else:
        raise ValueError(f"Invalid member name '{name}' according to JSON:API specification.")

    # Check for reserved characters
    for char in name:
        if char in reserved_characters:
            raise ValueError(f"Member name '{name}' contains reserved character '{char}' which is not allowed.")


NonEmptyStr = Annotated[str, constr(strip_whitespace=True, min_length=1)]


class ResourceIdentifierObject(BaseModel):
    """ResourceIdentifierObject enforces a resource identifier in a JSON:API document.

    Refer to https://jsonapi.org/format/#auto-id--link-objects for more information.
    Note that extra members are allowed in the ResourceIdentifierObject.

    Required fields:
        type (NonEmptyStr): The type of the resource.

    Optional fields:
        id (NonEmptyStr): The id of the resource.
        lid (NonEmptyStr): A locally unique identifier for the resource.
        meta (dict): a meta object containing non-standard meta-information about the resource.

    Raises:
        ValueError: ensure at least 'id' or 'lid' are present.
        ValueError: ensure 'type' is a string.
        ValueError: ensure 'id' and 'lid' are strings, if present.

    Returns:
        ResourceIdentifierObject: a validated ResourceIdentifierObject instance.
    """

    model_config = ConfigDict(extra='forbid')

    type_: NonEmptyStr = Field(..., alias='type')
    id_: NonEmptyStr | None = Field(None, alias='id')
    lid: NonEmptyStr | None = None
    meta: dict[str, Any] | None = None

    @model_validator(mode='after')
    def validate_id_or_lid(self) -> ResourceIdentifierObject:
        """Check that the ResourceIdentifierObject has either id or lid."""
        if not self.id_ and not self.lid:
            raise ValueError("ResourceIdentifierObject must have either 'id' or 'lid'.")

        # Ensure type_ is a string
        if not isinstance(self.type_, str) and not bool(self.type_):
            raise ValueError("'type' must be a string.")

        # Ensure id_ and lid, if present, are strings
        if self.id_ is not None and isinstance(self.id_, str) and not bool(self.id_):
            raise ValueError("'id' must be a string.")
        if self.lid is not None and isinstance(self.lid, str) and not bool(self.lid):
            raise ValueError("'lid' must be a string.")

        return self


class LinkObject(BaseModel):
    """LinkObject enforces a link in a JSON:API document.

    Refer to https://jsonapi.org/format/#auto-id--link-objects for more information.

    Required fields:
        href (HttpUrl): The URL of the link.

    Optional fields:
        rel (str): a string indicating the link's relation type. The string MUST be a valid link relation type.
        describedby (HttpUrl): a link to a description document (e.g. OpenAPI or JSON Schema) for the link target.
        title (str): a string which serves as a label for the destination of a link such that it can be used as a
            human-readable identifier (e.g., a menu entry).
        type (str): a string indicating the media type of the link's target.
        hreflang (str | list[str]): a string or an array of strings indicating the language(s) of the link's target.
            An array of strings indicates that the link's target is available in multiple languages. Each string
            MUST be a valid language tag [RFC5646].
        meta (dict): a meta object containing non-standard meta-information about the link.

    Raises:
        ValueError: href and describedby are invalid URIs.
        ValueError: each hreflang language tag is valid according to RFC 5646.
        ValueError: ensure type and rel fields are strings, if present.

    Returns:
        LinkObject: a validated LinkObject instance.
    """

    model_config = ConfigDict(extra='forbid')

    href: HttpUrl
    rel: NonEmptyStr | None = None
    describedby: HttpUrl | None = None
    title: NonEmptyStr | None = None
    type_: NonEmptyStr | None = Field(None, alias='type')
    hreflang: Annotated[list[NonEmptyStr], conlist(NonEmptyStr, min_length=1)] | NonEmptyStr | None = None
    meta: dict[str, Any] | None = None

    @model_validator(mode='after')
    def validate_link_object(self) -> LinkObject:
        """Validate the LinkObject according to the JSON:API spec."""
        # If 'rel' is present, ensure it's a valid relation type (simple string validation)
        if self.rel is not None and bool(self.rel):
            if not isinstance(self.rel, str):
                raise ValueError("'rel' must be a string indicating the link's relation type.")
            if not self.rel.isalnum():
                raise ValueError("'rel' must be a valid link relation type (alphanumeric characters only).")

        # hreflang: a string or an array of strings indicating the language(s) of the
        # link's target. An array of strings indicates that the link's target is available
        # in multiple languages. Each string MUST be a valid language tag [RFC5646].
        if self.hreflang is not None:
            if not bool(self.hreflang) and isinstance(self.hreflang, list | str):
                raise ValueError("'hreflang' must be a non-empty string or a list of non-empty strings.")
            elif isinstance(self.hreflang, str) and not self._is_valid_language_tag(self.hreflang):
                raise ValueError(f"'hreflang' must be a valid language tag. Got: {self.hreflang}")
            elif isinstance(self.hreflang, list):
                if len(self.hreflang) == 0:
                    raise ValueError("'hreflang' must be a non-empty list of language tags.")
                for lang in self.hreflang:
                    if not isinstance(lang, str):
                        raise ValueError(f"Each 'hreflang' entry must be a string. Got: {lang}")
                    if not self._is_valid_language_tag(lang):
                        raise ValueError(f"'hreflang' must be a valid language tag. Got: {lang}")
            elif not isinstance(self.hreflang, str | list):
                raise ValueError("'hreflang' must be a string or a list of strings.")

        return self

    @staticmethod
    def _is_valid_language_tag(tag: str) -> bool:
        """Validate that the language tag conforms to RFC 5646.

        Ref: https://stackoverflow.com/a/38959322
        """
        # Simple regex for basic language tags (not exhaustive)
        pattern = re.compile(r'^[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?$')
        return bool(pattern.match(tag))


LinkValue = Union[str, LinkObject, None]  # noqa: UP007
"""LinkValue: a union type for link values in JSON:API documents.

Refer to https://jsonapi.org/format/#document-links for more information.

LinkValue can be one of the following types:
- str: a string whose value is a URI-reference [RFC3986 Section 4.1]
    pointing to the link's target,
- LinkObject: a LinkObject instance.
- None: a null value if the link does not exist.
"""


class RelationshipObject(BaseModel):
    """RelationshipObject enforces a relationship in a JSON:API document.

    Refer to https://jsonapi.org/format/#document-resource-object-relationships for more information.

    Please note that extra members are allowed in the RelationshipObject.

    Optional fields:
        links (dict): a links object containing links related to the resource.
        data (ResourceIdentifierObject | list[ResourceIdentifierObject]): resource linkage.
        meta (dict): a meta object containing non-standard meta-information about the relationship.

    Raises:
        ValueError: ensure at least one of 'links', 'data', or 'meta' is present.

    Returns:
        RelationshipObject: a validated RelationshipObject instance.
    """

    model_config = ConfigDict(extra='allow')

    links: dict[str, LinkValue] | None = None
    data: ResourceIdentifierObject | list[ResourceIdentifierObject] | None = None
    meta: dict[str, Any] | None = None

    @model_validator(mode='after')
    def validate_relationship(self) -> RelationshipObject:
        """Validate the RelationshipObject according to the JSON:API spec."""
        if not self.links and not self.data and not self.meta:
            raise ValueError("RelationshipObject must contain at least one of 'links', 'data', or 'meta'.")

        # Validate links if present
        if self.links:
            allowed_links = {'self', 'related', 'describedby'}
            for link_key, link_value in self.links.items():
                if link_key not in allowed_links:
                    raise ValueError(
                        f"Invalid link key '{link_key}' in RelationshipObject. Allowed keys: {allowed_links}."
                    )
                if link_value is not None and not isinstance(link_value, str | LinkObject):
                    raise ValueError(f"Link '{link_key}' must be a string URI, LinkObject, or null.")
                if isinstance(link_value, str) and not is_valid_uri(link_value):
                    raise ValueError(f"Link '{link_key}' must be a valid URI-reference.")

        # Validate data linkage
        if self.data:
            if isinstance(self.data, list):
                for item in self.data:
                    if not isinstance(item, ResourceIdentifierObject):
                        raise ValueError("All items in 'data' must be ResourceIdentifierObject instances.")
            elif not isinstance(self.data, ResourceIdentifierObject):
                raise ValueError(
                    "'data' must be a ResourceIdentifierObject or a list of ResourceIdentifierObject instances."
                )

        # Validate member names if extra members are present
        extra_members = self.model_fields_set - set(self.model_fields.keys())
        if extra_members:
            for member_name in extra_members:
                validate_member_name(member_name)

        return self


class ResourceObject(BaseModel):
    """ResourceObject enforces a resource object in a JSON:API document.

    Refer to https://jsonapi.org/format/#document-resource-objects for more information.
    Note that extra members are not allowed in the ResourceObject.

    Required fields:
        type (str): The type of the resource.

    Optional fields:
        id (str): The id of the resource.
        lid (str): A locally unique identifier for the resource.
        attributes (dict): an attributes object representing some of the resource's data.
        relationships (dict): a relationships object describing relationships between the resource and other resources.
        links (dict): a links object containing links related to the resource.
        meta (dict): a meta object containing non-standard meta-information about the resource.

    Raises:
        ValueError: ensure 'type' is a string.
        ValueError: ensure either 'id' or 'lid' is present.
        ValueError: ensure 'id' or 'lid' are strings, if present.
        ValueError: ensure no field name conflicts between attributes and relationships.
        ValueError: ensure attribute keys do not include 'type', 'id', 'lid'.
        ValueError: ensure relationship keys do not include 'type', 'id', 'lid'.
        ValueError: ensure no foreign keys in attributes (e.g., 'author_id').
        ValueError: ensure all included resources are reachable from primary data.
        ValueError: ensure all included resources are unique.
        ValueError: ensure all included resources are linked from primary data.
        ValueError: ensure links are valid URIs.
        ValueError: ensure links are valid LinkObjects.
        ValueError: ensure links are valid keys ('self', 'related', 'describedby', 'pagination').
        ValueError: ensure 'lid' is unique within the document.

    Returns:
        ResourceObject: a validated ResourceObject instance.
    """

    model_config = ConfigDict(extra='forbid')

    type_: NonEmptyStr = Field(..., alias='type')
    id_: NonEmptyStr | None = Field(None, alias='id')
    lid: NonEmptyStr | None = None
    attributes: dict[str, Any] | None = None
    relationships: dict[str, RelationshipObject] | None = None
    links: dict[str, LinkValue] | None = None
    meta: dict[str, Any] | None = None

    @model_validator(mode='after')
    def validate_resource_object(self) -> ResourceObject:
        """Validate the ResourceObject according to the JSON:API spec."""
        # Ensure type_ is a string
        if not isinstance(self.type_, str) or not bool(self.type_):
            raise ValueError("'type' must be a string.")

        # Ensure id_ and lid, if present, are strings
        if self.id_ is not None and isinstance(self.id_, str) and not bool(self.id_):
            raise ValueError("'id' must be a string.")
        if self.lid is not None and isinstance(self.lid, str) and not bool(self.lid):
            raise ValueError("'lid' must be a string.")

        # Either id or lid must be present
        if (not self.id_ or not bool(self.id_)) and (not self.lid or not bool(self.lid)):
            raise ValueError("ResourceObject must have either 'id' or 'lid'.")

        # Ensure no field name conflicts
        if self.attributes and self.relationships:
            attribute_keys = set(self.attributes.keys())
            relationship_keys = set(self.relationships.keys())
            common_keys = attribute_keys.intersection(relationship_keys)
            reserved_keys = {'type', 'id', 'lid'}
            conflicting_reserved_keys = common_keys.intersection(reserved_keys)
            if conflicting_reserved_keys:
                raise ValueError(
                    f'Fields {conflicting_reserved_keys} are reserved and cannot be used as attribute or relationship names.'  # noqa: E501
                )
            if common_keys:
                raise ValueError(
                    f'Attribute and relationship names must not conflict. Conflicting names: {common_keys}'
                )

        # Validate attributes
        if self.attributes:
            # Ensure attribute keys do not include 'type', 'id', 'lid'
            reserved_keys = {'type', 'id', 'lid'}
            attribute_keys = set(self.attributes.keys())
            if reserved_keys.intersection(attribute_keys):
                raise ValueError(
                    f'Attribute names {reserved_keys.intersection(attribute_keys)} are reserved and cannot be used.'
                )

            # Enforce that attribute keys do not contain foreign keys (e.g., 'author_id')
            foreign_keys = {key for key in attribute_keys if key.endswith('_id')}
            if foreign_keys:
                raise ValueError(
                    f'Attribute names {foreign_keys} are reserved for relationships and should not appear in attributes.'  # noqa: E501
                )

        # Validate relationships
        if self.relationships:
            # Ensure relationship keys do not include 'type', 'id', 'lid'
            reserved_keys = {'type', 'id', 'lid'}
            relationship_keys = set(self.relationships.keys())
            if reserved_keys.intersection(relationship_keys):
                raise ValueError(
                    f'Relationship names {reserved_keys.intersection(relationship_keys)} are reserved and cannot be used.'  # noqa: E501
                )

        # Validate links if present
        if self.links:
            allowed_links = {'self', 'related', 'describedby', 'pagination'}
            for link_key, link_value in self.links.items():
                if link_key not in allowed_links:
                    raise ValueError(f"Invalid link key '{link_key}' in ResourceObject. Allowed keys: {allowed_links}.")
                if link_value is not None and not isinstance(link_value, str | LinkObject):
                    raise ValueError(f"Link '{link_key}' must be a string URI, LinkObject, or null.")
                if isinstance(link_value, str) and not is_valid_uri(link_value):
                    raise ValueError(f"Link '{link_key}' must be a valid URI-reference.")
                if isinstance(link_value, LinkObject):
                    link_value = LinkObject(**link_value.dict())  # Ensure LinkObject validation

        return self

    @classmethod
    def from_model(
        cls,
        model: BaseModel,
        type_: str | None = None,
        id_: str | None = None,
        relationships: dict[str, RelationshipObject] | None = None,
        links: dict[str, Any] | None = None,
        meta: dict[str, Any] | None = None,
        lid_registry: dict[Any, str] | None = None,
    ) -> ResourceObject:
        """Create a ResourceObject from a Pydantic BaseModel instance."""

        if lid_registry is None:
            lid_registry = {}

        # Get 'id' and 'type' from the model if not provided
        if id_ is None and hasattr(model, 'id'):
            id_ = str(model.id)

        if type_ is None and hasattr(model, '__type__'):
            type_ = model.__type__

        if type_ is None:
            raise ValueError(
                "Resource 'type' must be provided either as a parameter or via '__type__' attribute in the model."
            )

        # Extract attributes from the model, excluding 'id' and 'type' if present
        exclude_fields = {'id', 'type'} if hasattr(model, 'type') else {'id'}
        attributes = model.model_dump(exclude=exclude_fields)

        # Generate or retrieve 'lid' if 'id' is not available
        lid = None
        if id_ is None:
            model_id = id(model)  # Use the unique id of the model instance
            if model_id in lid_registry:
                lid = lid_registry[model_id]
            else:
                # Generate a new 'lid' and store it in the registry
                lid = str(uuid.uuid4())
                lid_registry[model_id] = lid

        return cls(
            type=type_,
            id=id_,
            lid=lid,
            attributes=attributes if attributes else None,
            relationships=relationships,
            links=links,
            meta=meta,
        )


# Primary data as per JSON:API spec
PrimaryData = Union[  # noqa: UP007
    ResourceObject, ResourceIdentifierObject, list[ResourceObject], list[ResourceIdentifierObject], None
]


ALLOWED_JSONAPI_VERSIONS = ('1.0', '1.1')


class JSONAPIObject(BaseModel):
    """JSONAPIObject enforces the JSON:API version in a JSON:API document.

    Refer to https://jsonapi.org/format/#document-jsonapi-object for more information.

    Required fields:
        version (str): The JSON:API version. Default is '1.1'.

    Optional fields:
        meta (dict): a meta object containing non-standard meta-information about the JSON:API document.

    Raises:
        ValueError: ensure 'version' is one of the allowed JSON:API versions.

    Returns:
        JSONAPIObject: a validated JSONAPIObject instance.
    """

    version: str = '1.1'
    meta: dict[str, Any] | None = None

    @field_validator('version')
    @classmethod
    def must_have_correct_version(cls, v: str) -> Any:
        """Validate the 'version' field according to the JSON:API spec."""
        if v not in ALLOWED_JSONAPI_VERSIONS:
            raise ValueError(f"JSONAPI 'version' must be one of {ALLOWED_JSONAPI_VERSIONS}.")
        return v


class Document(BaseModel):
    model_config = ConfigDict(extra='allow')

    data: PrimaryData = None
    errors: list[Any] | None = None  # Error objects can be further defined
    meta: dict[str, Any] | None = None
    jsonapi: JSONAPIObject | None = None
    links: dict[str, LinkValue] | None = None
    included: list[ResourceObject] | None = None

    @model_validator(mode='after')
    def validate_document(self) -> Document:
        """Validate the Document according to the JSON:API spec."""

        # 1. The members 'data' and 'errors' MUST NOT coexist in the same document.
        if self.data is not None and self.errors is not None:
            raise ValueError("The members 'data' and 'errors' MUST NOT coexist in the same document.")

        # 2. A document MUST contain at least one of the following top-level members: data, errors, meta
        if self.data is None and self.errors is None and self.meta is None and self.jsonapi is None:
            raise ValueError("A document MUST contain at least one of 'data', 'errors', 'meta', or 'jsonapi'.")

        # 3. If a document does not contain a top-level 'data' key, the 'included' member MUST NOT be present either.
        if self.data is None and self.included is not None:
            raise ValueError(
                "If a document does not contain a top-level 'data' key, the 'included' member MUST NOT be present."
            )

        # 4. Validate extra members in the document
        extra_members = self.model_fields_set - set(self.model_fields.keys())
        if extra_members:
            for member_name in extra_members:
                validate_member_name(member_name)

        # 5. Validate 'data' types according to the spec
        if self.data is not None:
            valid_types = (ResourceObject, ResourceIdentifierObject)
            if isinstance(self.data, list):
                if not all(isinstance(item, valid_types) for item in self.data):
                    raise TypeError(
                        "All items in 'data' must be 'ResourceObject' or 'ResourceIdentifierObject' instances."
                    )
            elif not isinstance(self.data, valid_types):
                raise TypeError("'data' must be a 'ResourceObject', 'ResourceIdentifierObject', or a list of them.")

        # 6. Validate 'included' types
        if self.included is not None:
            if not isinstance(self.included, list):
                raise TypeError("'included' must be a list of 'ResourceObject' instances.")
            if not all(isinstance(item, ResourceObject) for item in self.included):
                raise TypeError("All items in 'included' must be 'ResourceObject' instances.")

            # 7. Ensure uniqueness in 'included' (no duplicates by type and id/lid)
            seen_resources: set[tuple[str, str | None]] = set()
            for resource in self.included:
                identifier = (resource.type_, resource.id_) if resource.id_ else (resource.type_, resource.lid)
                if identifier in seen_resources:
                    raise ValueError(
                        f"Duplicate resource in 'included': type='{resource.type_}', id='{resource.id_}' or lid='{resource.lid}'."  # noqa: E501
                    )
                seen_resources.add(identifier)

            # 8. Ensure all included resources are linked from primary data
            # Build a set of all reachable resource identifiers from 'data'
            reachable_resources: set[tuple[str, str | None]] = set()
            self._traverse_relationships(self.data, reachable_resources)

            # Collect all included resource identifiers
            included_resources: set[tuple[str, str | None]] = set()
            for resource in self.included:
                identifier = (resource.type_, resource.id_) if resource.id_ else (resource.type_, resource.lid)
                included_resources.add(identifier)

            # Check that all included resources are reachable
            unreachable = included_resources - reachable_resources
            if unreachable:
                raise ValueError(f'Included resources are not reachable from primary data: {unreachable}')

        # 9. Validate links if present
        if self.links:
            allowed_links = {'self', 'related', 'describedby'}
            for link_key, link_value in self.links.items():
                if link_key not in allowed_links:
                    raise ValueError(f"Invalid link key '{link_key}' in Document. Allowed keys: {allowed_links}.")
                if link_value is not None and not isinstance(link_value, str | LinkObject):
                    raise ValueError(f"Link '{link_key}' must be a string URI, LinkObject, or null.")
                if isinstance(link_value, str) and not is_valid_uri(link_value):
                    raise ValueError(f"Link '{link_key}' must be a valid URI-reference.")
                if isinstance(link_value, LinkObject):
                    link_value = LinkObject(**link_value.model_dump())  # Ensure LinkObject validation

        return self

    def _traverse_relationships(
        self,
        data: PrimaryData,
        reachable: set[tuple[str, str | None]],
        visited: set[tuple[str, str | None]] | None = None,
    ) -> None:
        """Recursively traverse relationships to find all reachable resources."""
        if visited is None:
            visited = set()

        if data is None:
            return

        resources: list[Any] = []
        if isinstance(data, list):
            resources = data
        else:
            resources = [data]

        for resource in resources:
            identifier = (resource.type_, resource.id_) if resource.id_ else (resource.type_, resource.lid)
            if identifier in visited:
                continue
            visited.add(identifier)
            reachable.add(identifier)

            if isinstance(resource, ResourceObject) and resource.relationships:
                for rel in resource.relationships.values():
                    if rel.data:
                        if isinstance(rel.data, list):
                            self._traverse_relationships(rel.data, reachable, visited)
                        else:
                            self._traverse_relationships(rel.data, reachable, visited)


# Rebuild models to resolve forward references (if any)
ResourceIdentifierObject.model_rebuild()
LinkObject.model_rebuild()
RelationshipObject.model_rebuild()
ResourceObject.model_rebuild()
JSONAPIObject.model_rebuild()
Document.model_rebuild()
