class AuthenticationError(Exception):
    """Raised when authentication fails (invalid credentials)"""

    pass


class InvalidTokenError(Exception):
    """Raised when token is invalid or expired"""

    pass
