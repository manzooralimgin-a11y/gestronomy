class GastronomyError(Exception):
    def __init__(self, detail: str = "An error occurred") -> None:
        self.detail = detail
        super().__init__(self.detail)


class NotFoundError(GastronomyError):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail)


class DuplicateError(GastronomyError):
    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(detail)


class ValidationError(GastronomyError):
    def __init__(self, detail: str = "Validation failed") -> None:
        super().__init__(detail)


class AuthorizationError(GastronomyError):
    def __init__(self, detail: str = "Not authorized") -> None:
        super().__init__(detail)


class ExternalServiceError(GastronomyError):
    def __init__(self, detail: str = "External service error") -> None:
        super().__init__(detail)
