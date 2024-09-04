from typing import Any

from pyjas.core.classes import URL
from pyjas.core.exceptions import PyJASException
from pyjas.core.util import is_valid_hreflang


class JsonAPILinksObject:
    """A class to represent a JSON API link object.

    Reference: https://jsonapi.org/format/#auto-id--link-objects

    Args:
        href (str | URL): The link that generated the current response document. a string whose value is a URI-reference [RFC3986 Section 4.1] pointing to the link's target.
        rel (str | None): A string indicating the link's relation type. The string MUST be a valid link relation type.
        described_by (str | URL | None): The link to a description document for the current document. a link to a description document (e.g. OpenAPI or JSON Schema) for the link target.
        title (str | None): The title of the link. a string which serves as a label for the destination of a link such that it can be used as a human-readable identifier (e.g., a menu entry).
        media_type (str | None): The media type of the link. a string indicating the media type of the link's target.
        hreflang (str | list[str] | None): The language of the link. a string or an array of strings indicating the language(s) of the link's target. An array of strings indicates that the link's target is available in multiple languages. Each string MUST be a valid language tag [RFC5646].
        meta (dict[str, Any] | None): The meta information of the link. a meta object containing non-standard meta-information about the link.
    """  # noqa: E501

    def __init__(
        self,
        href: str | URL,
        rel: str | None = None,
        described_by: str | URL | None = None,
        title: str | None = None,
        media_type: str | None = None,
        hreflang: str | list[str] | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        # Required attributes
        self.href = href

        # Optional attributes
        self.rel = rel
        self.described_by = described_by
        self.title = title
        self.media_type = media_type
        self.hreflang = hreflang
        self.meta = meta

        # Validate the object
        self._validate()

    def _validate(self) -> None:
        for link in [self.href, self.described_by]:
            if link is not None and not isinstance(link, str):
                raise PyJASException('Links must be of type str, URL, or None.')
        if not is_valid_hreflang(self.hreflang):
            raise PyJASException('The hreflang attribute must be a valid language tag.')

    def to_dict(self) -> dict:
        """Returns the link as a dictionary."""
        link = {
            'href': str(self.href),
            'rel': self.rel,
            'describedBy': str(self.described_by) if self.described_by else None,
            'title': self.title,
            'mediaType': self.media_type,
            'hreflang': self.hreflang,
            'meta': self.meta,
        }

        return {k: v for k, v in link.items() if v is not None}

    def __repr__(self):
        return (
            f'JsonAPILinksObject(href={self.href}, rel={self.rel}, described_by={self.described_by}, '
            f'title={self.title}, media_type={self.media_type}, hreflang={self.hreflang}, meta={self.meta})'
        )

    @classmethod
    def builder(cls) -> 'JsonAPILinksBuilder':
        """Returns a new instance of JsonAPILinksBuilder."""
        return JsonAPILinksBuilder()


class JsonAPILinksBuilder:
    """A class to build a JSON API link object."""

    def __init__(self, href: str | URL) -> None:
        self._href = href
        self._rel = None
        self._described_by = None
        self._title = None
        self._media_type = None
        self._hreflang = None
        self._meta = None

    @staticmethod
    def _convert_str_to_url(value: str | URL) -> URL | str:
        if isinstance(value, str):
            try:
                return URL(value)
            except ValueError:
                return value
        return value

    @property
    def href(self) -> str | URL:
        """str | URL: Gets the link that generated the current response document."""
        return self._href

    @href.setter
    def set_href(self, value: str | URL) -> None:
        """Sets the link that generated the current response document."""
        if not value:
            raise ValueError('The href attribute must be set.')
        self._href = self._convert_str_to_url(value)

    @property
    def rel(self) -> str | None:
        """str | None: Gets the related resource link when the primary data represents a resource relationship."""
        return self._rel

    @rel.setter
    def set_rel(self, value: str | None) -> None:
        """Sets the related resource link when the primary data represents a resource relationship."""
        self._rel = value

    @property
    def described_by(self) -> str | URL | None:
        """str | URL | None: Gets the link to a description document for the current document."""
        return self._described_by

    @described_by.setter
    def set_described_by(self, value: str | URL | None) -> None:
        """Sets the link to a description document for the current document."""
        self._described_by = self._convert_str_to_url(value)

    @property
    def title(self) -> str | None:
        """str | None: Gets the title of the link."""
        return self._title

    @title.setter
    def set_title(self, value: str | None) -> None:
        """Sets the title of the link."""
        self._title = value

    @property
    def media_type(self) -> str | None:
        """str | None: Gets the media type of the link."""
        return self._media_type

    @media_type.setter
    def set_media_type(self, value: str | None) -> None:
        """Sets the media type of the link."""
        self._media_type = value

    @property
    def hreflang(self) -> str | list[str] | None:
        """str | list[str] | None: Gets the language of the link."""
        return self._hreflang

    @hreflang.setter
    def set_hreflang(self, value: str | list[str] | None) -> None:
        """Sets the language of the link."""
        self._hreflang = value

    @property
    def meta(self) -> dict[str, Any] | None:
        """dict[str, Any] | None: Gets the meta information of the link."""
        return self._meta

    @meta.setter
    def set_meta(self, value: dict[str, Any] | None) -> None:
        """Sets the meta information of the link."""
        self._meta = value

    def build(self) -> JsonAPILinksObject:
        """Returns a new instance of JsonAPILinksObject."""
        return JsonAPILinksObject(
            href=self._href,
            rel=self._rel,
            described_by=self._described_by,
            title=self._title,
            media_type=self._media_type,
            hreflang=self._hreflang,
            meta=self._meta,
        )


# Attribute type for the links attribute in a JSON API document
JsonAPILinksType = dict[str, str | None | JsonAPILinksObject]


class JsonAPIPaginationLinksObject:
    """A class to represent JSON API pagination links."""

    def __init__(
        self,
        first: str | URL | None = None,
        last: str | URL | None = None,
        prev: str | URL | None = None,
        next_: str | URL | None = None,
    ) -> None:
        self.first = first
        self.last = last
        self.prev = prev
        self.next_ = next_

        # Validate the pagination links
        self._validate()

    def _validate(self) -> None:
        """Validates the pagination links."""
        for link in [self.first, self.last, self.prev, self.next_]:
            if link is not None and not isinstance(link, str | URL):
                raise PyJASException('Pagination links must be of type str, URL, or None.')

    def to_dict(self) -> dict:
        """Returns the pagination links as a dictionary."""
        return {
            'first': str(self.first) if self.first else None,
            'last': str(self.last) if self.last else None,
            'prev': str(self.prev) if self.prev else None,
            'next': str(self.next_) if self.next_ else None,
        }

    def __repr__(self):
        return (
            f'JsonAPIPaginationLinksObject(first={self.first}, last={self.last}, prev={self.prev}, next_={self.next_})'
        )


class JsonAPITopLevelLinksObject(JsonAPIPaginationLinksObject):
    """A class to represent a JSON API top-level links object."""

    def __init__(
        self,
        self_: str | URL | JsonAPILinksObject | None = None,
        related: str | URL | JsonAPILinksObject | None = None,
        described_by: str | URL | JsonAPILinksObject | None = None,
        first: str | URL | None = None,
        last: str | URL | None = None,
        prev: str | URL | None = None,
        next_: str | URL | None = None,
    ) -> None:
        # Required attributes
        self.self_ = self_
        self.related = related
        self.described_by = described_by

        # Initialize pagination links
        super().__init__(first, last, prev, next_)

        # Validate the object
        self._validate()

    def _validate(self) -> None:
        for link in [self.self_, self.related, self.described_by]:
            if link is not None and not isinstance(link, str | URL | JsonAPILinksObject):
                raise PyJASException('Links must be of type str, URL, JsonAPILinksObject, or None.')

    def to_dict(self) -> dict:
        """Returns the top-level links as a dictionary, including pagination links."""
        top_level_links = {
            'self': str(self.self_) if self.self_ else None,
            'related': str(self.related) if self.related else None,
            'describedBy': str(self.described_by) if self.described_by else None,
        }
        # Add pagination links
        top_level_links.update(super().to_dict())
        return {k: v for k, v in top_level_links.items() if v is not None}

    def __repr__(self):
        return (
            f'JsonAPITopLevelLinksObject(self_={self.self_}, related={self.related}, described_by={self.described_by}, '
            f'first={self.first}, last={self.last}, prev={self.prev}, next_={self.next_})'
        )
