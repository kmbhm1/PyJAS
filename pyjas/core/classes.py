import json
from typing import Any


class JsonAPISpecificationObject:
    """A class that provides methods to convert the object to a JSON string and vice versa."""

    def to_json(self) -> str:
        """Converts the object to a JSON string."""
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        """Converts the object to a dictionary."""
        return self.__dict__

    @classmethod
    def from_json(cls, data: str) -> 'JsonAPISpecificationObject':
        """Converts a JSON string to an object."""
        return cls(**json.loads(data))

    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        return f'{self.__class__.__name__}({self.to_dict()})'
