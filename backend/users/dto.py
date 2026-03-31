from dataclasses import asdict, dataclass


@dataclass(slots=True)
class BaseAuthResponse:
    """Base DTO containing user identity fields returned after authentication."""

    username: str
    email: str

    def to_dict(self):
        """Return a dict representation of the dataclass."""
        return asdict(self)


@dataclass(slots=True)
class JWTAuthResponse(BaseAuthResponse):
    """JWT-specific auth response including access and refresh tokens."""

    access: str
    refresh: str
