class APIError(Exception):
    """Base API error"""
    def __init__(self, message, code='API_ERROR', status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message, code='VALIDATION_ERROR'):
        super().__init__(message, code, 400)

class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message, code='AUTHENTICATION_ERROR'):
        super().__init__(message, code, 401)

class AuthorizationError(APIError):
    """Authorization error"""
    def __init__(self, message, code='AUTHORIZATION_ERROR'):
        super().__init__(message, code, 403)

class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message, code='NOT_FOUND'):
        super().__init__(message, code, 404)

class ConflictError(APIError):
    """Conflict error"""
    def __init__(self, message, code='CONFLICT'):
        super().__init__(message, code, 409)

class RateLimitError(APIError):
    """Rate limit exceeded"""
    def __init__(self, message='Too many requests', code='RATE_LIMIT_EXCEEDED'):
        super().__init__(message, code, 429)
