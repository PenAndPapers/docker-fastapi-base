from fastapi import HTTPException


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)


class BadRequestError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=403, detail=detail)


class ValidationError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


class DatabaseError(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)
