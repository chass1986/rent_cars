class CustomException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code


class MissingMandatoryFields(CustomException):
    pass


class PasswordsNotMatching(CustomException):
    pass


class WrongFormat(CustomException):
    pass


class InputNotAcceptable(CustomException):
    pass


class RecordAlreadyExists(CustomException):
    pass


class RecordNotFound(CustomException):
    pass


class WrongType(CustomException):
    pass
