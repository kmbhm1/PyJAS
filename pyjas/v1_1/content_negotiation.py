from typing import Any
from urllib.parse import urlparse

# Custom Exceptions


class ContentTypeError(Exception):
    """Custom exception for content type errors."""

    pass


class AcceptHeaderError(Exception):
    """Custom exception for accept header errors."""

    pass


# Content Type Class


class ContentType:
    MEDIA_TYPE = 'application/vnd.api+json'
    ALLOWED_PARAMS = {'ext', 'profile'}

    def __init__(self, media_type: str, params: dict[str, list[str]]):
        self.media_type = media_type
        self.params = params
        self.validate()

    @classmethod
    def parse(cls, content_type_str: str) -> 'ContentType':
        """Parse a content type string and return a ContentType instance."""
        # Split media type and parameters
        parts = [part.strip() for part in content_type_str.split(';') if part.strip()]
        if not parts:
            raise ContentTypeError('Content-Type header is empty.')

        media_type = parts[0]
        params = {}
        for param in parts[1:]:
            if '=' not in param:
                raise ContentTypeError(f"Invalid parameter format: '{param}'")
            key, value = param.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"')  # Remove surrounding quotes

            if key not in cls.ALLOWED_PARAMS:
                raise ContentTypeError(f"Invalid parameter '{key}'. Only 'ext' and 'profile' are allowed.")

            # Split value by spaces to get list of URIs
            uris = value.split()
            # Validate URIs
            for uri in uris:
                if not cls._is_valid_uri(uri):
                    raise ContentTypeError(f"Invalid URI in '{key}': '{uri}'")
            params[key] = uris

        return cls(media_type=media_type, params=params)

    def validate(self) -> None:
        """Validate the media type and parameters according to the JSON:API spec."""
        # Validate media type
        if self.media_type != self.MEDIA_TYPE:
            raise ContentTypeError(f"Invalid media type '{self.media_type}'. Expected '{self.MEDIA_TYPE}'.")

        # Validate parameters
        for key in self.params.keys():
            if key not in self.ALLOWED_PARAMS:
                raise ContentTypeError(f"Invalid parameter '{key}'. Only 'ext' and 'profile' are allowed.")

        # Ensure parameter values are lists of URIs
        for key, uris in self.params.items():
            if not isinstance(uris, list):
                raise ContentTypeError(f"The value of '{key}' must be a list of URIs.")
            for uri in uris:
                if not self._is_valid_uri(uri):
                    raise ContentTypeError(f"Invalid URI in '{key}': '{uri}'")

    @staticmethod
    def _is_valid_uri(uri: str) -> bool:
        """Check if a string is a valid URI."""
        result = urlparse(uri)
        return all([result.scheme, result.netloc])

    @property
    def extensions(self) -> list[str]:
        """Return the list of extension URIs."""
        return self.params.get('ext', [])

    @property
    def profiles(self) -> list[str]:
        """Return the list of profile URIs."""
        return self.params.get('profile', [])

    def to_string(self) -> str:
        """Serialize the ContentType back to a string."""
        parts = [self.media_type]
        for key in sorted(self.params.keys()):
            # Join URIs with spaces
            value = ' '.join(self.params[key])
            # Surround value with quotes
            parts.append(f'{key}="{value}"')
        return '; '.join(parts)

    @classmethod
    def create(
        cls,
        extensions: list[str] | None = None,
        profiles: list[str] | None = None,
    ) -> 'ContentType':
        """Create a ContentType instance with the given extensions and profiles."""
        params = {}
        if extensions:
            for uri in extensions:
                if not cls._is_valid_uri(uri):
                    raise ContentTypeError(f"Invalid URI in 'extensions': '{uri}'")
            params['ext'] = extensions
        if profiles:
            for uri in profiles:
                if not cls._is_valid_uri(uri):
                    raise ContentTypeError(f"Invalid URI in 'profiles': '{uri}'")
            params['profile'] = profiles
        return cls(media_type=cls.MEDIA_TYPE, params=params)


# Content Negotiation Class


class ContentNegotiation:
    """Class to handle content negotiation according to the JSON:API specification."""

    def __init__(self, supported_extensions: list[str] | None = None):
        """Initialize with the list of supported extension URIs."""
        self.supported_extensions = set(supported_extensions or [])

    def validate_content_type_header(self, content_type_str: str) -> None:
        """Validate the Content-Type header of a request.

        Raises:
            ContentTypeError: If the Content-Type header is invalid.
        """
        try:
            content_type = ContentType.parse(content_type_str)
        except ContentTypeError as e:
            raise ContentTypeError(f'Invalid Content-Type header: {e}')

        # Check for unsupported parameters
        unsupported_params = set(content_type.params.keys()) - ContentType.ALLOWED_PARAMS
        if unsupported_params:
            raise ContentTypeError(
                f"Invalid parameter(s) in Content-Type header: {', '.join(unsupported_params)}. "
                f"Only 'ext' and 'profile' are allowed."
            )

        # Check for unsupported extensions
        if 'ext' in content_type.params:
            unsupported_exts = set(content_type.extensions) - self.supported_extensions
            if unsupported_exts:
                raise ContentTypeError(
                    f"Unsupported extension(s) in Content-Type header: {', '.join(unsupported_exts)}"
                )

    def validate_accept_header(self, accept_header: str) -> None:
        """Validate the Accept header of a request.

        Raises:
            AcceptHeaderError: If the Accept header is invalid or not acceptable.
        """
        # Parse the Accept header
        media_ranges = self._parse_accept_header(accept_header)
        jsonapi_media_types = [
            media_range for media_range in media_ranges if media_range['media_type'] == ContentType.MEDIA_TYPE
        ]

        # Remove media types with invalid parameters
        valid_media_types = []
        for media_range in jsonapi_media_types:
            params = media_range['params']
            invalid_params = set(params.keys()) - ContentType.ALLOWED_PARAMS
            if invalid_params:
                # Ignore this media type as per spec
                continue
            else:
                valid_media_types.append(media_range)

        if not valid_media_types:
            raise AcceptHeaderError('No acceptable media types found in Accept header.')

        # Check for unsupported extensions
        all_exts_unsupported = True
        for media_range in valid_media_types:
            exts = media_range['params'].get('ext', [])
            if not exts or set(exts).issubset(self.supported_extensions):
                all_exts_unsupported = False
                break

        if all_exts_unsupported:
            raise AcceptHeaderError('No acceptable media types found due to unsupported extensions.')

    def generate_vary_header(self) -> str:
        """Generate the Vary header.

        Returns:
            str: The Vary header value.
        """
        return 'Accept'

    def _parse_accept_header(self, accept_header: str) -> list[dict[str, Any]]:
        """Parse the Accept header into a list of media ranges.

        Returns:
            List[Dict[str, Any]]: List of media ranges with media_type, q, and params.
        """
        media_ranges: list[dict[str, Any]] = []
        for media_range_str in accept_header.split(','):
            media_range_str = media_range_str.strip()
            if not media_range_str:
                continue
            # Split media type and parameters
            parts = [part.strip() for part in media_range_str.split(';') if part.strip()]
            media_type = parts[0]
            params = {}
            q = 1.0
            for param in parts[1:]:
                if '=' not in param:
                    continue
                key, value = param.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')  # Remove quotes
                if key == 'q':
                    try:
                        q = float(value)
                    except ValueError:
                        pass  # Ignore invalid q values
                else:
                    # Handle ext and profile parameters
                    if key in ContentType.ALLOWED_PARAMS:
                        uris = value.split()
                        params[key] = uris
            media_ranges.append({'media_type': media_type, 'q': q, 'params': params})

        # Sort by q value descending
        media_ranges.sort(key=lambda x: x['q'], reverse=True)  # mypy: ignore
        return media_ranges  # mypy: ignore
