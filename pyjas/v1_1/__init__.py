"""This module provides the classes and functions for JSON:API v1.1.

## Description

This module provides the following classes and functions:

- AcceptHeaderError: An exception class for an invalid Accept header.
- ContentNegotiation: A class for content negotiation with content types.
- ContentType: An class for a content type.
- ContentTypeError: An exception class for an invalid content type.
- Document: A class for a JSON:API document.
- JSONAPIObject: A class for a JSON:API "jsonapi" version information object.
- LinkObject: A class for a JSON:API link object.
- LinkValue: A class for a JSON:API link objects or url strings.
- PrimaryData: A class for a JSON:API document data types.
- RelationshipObject: A class for a JSON:API relationship object.
- ResourceIdentifierObject: A class for a JSON:API resource identifier object.
- ResourceObject: A class for a JSON:API resource object.
- ALLOWED_JSONAPI_VERSIONS: A tuple of allowed JSON:API versions.

"""

from .content_negotiation import AcceptHeaderError, ContentNegotiation, ContentType, ContentTypeError
from .jsonapi_builder import (
    ALLOWED_JSONAPI_VERSIONS,
    Document,
    JSONAPIObject,
    LinkObject,
    LinkValue,
    PrimaryData,
    RelationshipObject,
    ResourceIdentifierObject,
    ResourceObject,
)

__all__ = [
    'AcceptHeaderError',
    'ContentNegotiation',
    'ContentType',
    'ContentTypeError',
    'Document',
    'JSONAPIObject',
    'LinkObject',
    'LinkValue',
    'PrimaryData',
    'RelationshipObject',
    'ResourceIdentifierObject',
    'ResourceObject',
    'ALLOWED_JSONAPI_VERSIONS',
]
