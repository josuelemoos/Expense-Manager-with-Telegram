class ServiceError(Exception):
    status_code = 400

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class NotFoundError(ServiceError):
    status_code = 404


class ValidationError(ServiceError):
    status_code = 400
