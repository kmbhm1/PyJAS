from typing import Any

from pyjas.core.classes import URL


class JSONAPIImplementationObject:
    def __init__(
        self,
        ext: list[str | URL] | None = None,
        profile: list[str | URL] | None = None,
        meta: dict[str, Any] | None = None,
    ):
        self.version: str = '1.1'
        self.ext = ext
        self.profile = profile
        self.meta = meta

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JSONAPIImplementationObject):
            return NotImplemented
        return bool(self.to_dict() == other.to_dict())

    def to_dict(self) -> dict[str, Any]:
        """Returns the JSON API implementation object as a dictionary."""

        profiles = [str(p) for p in self.profile] if self.profile else None
        ext = [str(e) for e in self.ext] if self.ext else None

        d = {
            'version': self.version,
            'ext': profiles,
            'profile': ext,
            'meta': self.meta if self.meta else None,
        }

        return {k: v for k, v in d.items() if v is not None}
