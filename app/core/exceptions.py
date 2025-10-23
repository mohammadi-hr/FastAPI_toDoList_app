from fastapi import HTTPException

class AppException(Exception):
    def __init__(self, message:str, status_code:int = 400, error_code: str = "Error"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class NotFoundException(AppException):
    def __init__(self, message:str = "Resource not found"):
        super().__init__(message, status_code = 404, error_code= "Not Found")

class UnauthorizedException(AppException):
    def __init__(self, message:str = "Unauthorized"):
        super().__init__(message, status_code= 401, error_code= "Unauthorized")

class ForbiddenException(AppException):
    def __init__(self, message:str = "Forbidden"):
        super().__init__(message, status_code= 403, error_code= "Forbidden")