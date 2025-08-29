class UserException(Exception):
    def __init__(self, message: str = "A user-related error occurred"):
        self.message = message
        super().__init__(self.message)


class MissingCredentialsException(UserException):
    def __init__(self, message: str = "Missing credentials"):
        super().__init__(message)


class InvalidCredentialsException(UserException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)


class UserError(Exception):
    def __init__(self, message: str = "User error occurred"):
        self.message = message
        super().__init__(self.message)


def check_credentials(username: str, password: str):
    if not username or not password:
        raise MissingCredentialsException("Username and password are required")
    if len(password) < 8:
        raise InvalidCredentialsException("Password must be at least 8 characters long")
    return True

