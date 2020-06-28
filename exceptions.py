class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidCredentialsError(Exception):
    """Base class for other Studzone Credential related exceptions"""
    pass


class InvalidPasswordError(InvalidCredentialsError):
    """Raised when the ' Invalid Password' alert is detected in the Studzone Login response HTML"""
    pass


class InvalidUsernameError(InvalidCredentialsError):
    """Raised when the 'Invalid Login Id' alert is detected in the Studzone Login response HTML"""
    pass
