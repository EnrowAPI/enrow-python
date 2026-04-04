class EnrowError(Exception):
    def __init__(self, status: int, error: str, message: str):
        super().__init__(message)
        self.status = status
        self.error = error
        self.message = message


class AuthenticationError(EnrowError):
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(401, "Unauthorized", message)


class InsufficientBalanceError(EnrowError):
    def __init__(self, message: str = "Your credit balance is insufficient."):
        super().__init__(422, "InsufficientBalance", message)


class RateLimitError(EnrowError):
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        super().__init__(429, "RateLimitExceeded", message)
        self.retry_after = retry_after
