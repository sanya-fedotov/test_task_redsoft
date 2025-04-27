from fastapi import HTTPException, status


class PeopleException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class NotFindPersonException(PeopleException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"


class NotFindSurnameException(PeopleException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь с такой фамилией не найден"


class EmptyDatabaseException(PeopleException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пустая база данных"


class InvalidSurnameFormatException(PeopleException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Фамилия должна содержать только латиницу, дефисы или пробелы"


class InvalidPersonDataFormatException(PeopleException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "ФИО, национальность, пол должно содержать только латиницу, дефисы или пробелы"


class InvalidFullnameFormatException(PeopleException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "ФИО содержать только латиницу, дефисы или пробелы"


class EmailAlreadyExistsException(PeopleException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Этот email уже существует"


class CannotAddYourselfException(PeopleException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Нельзя добавить самого себя в друзья"


class NotFindPeopleException(PeopleException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Один или оба пользователя не найдены"


class AlreadyFriendsException(PeopleException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователи уже являются друзьями"


class InvalidAgeFormatException(PeopleException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Возраст не может быть отрицательным"


class MissingNameOrSurnameException(PeopleException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Необходимо заполнить имя и фамилию"


class IncorrectEmailOrPasswordException(PeopleException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный email или пароль"


class TokenAbsentException(PeopleException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(PeopleException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class TokenExpiredException(PeopleException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истек"


class UserIsNotPresent(PeopleException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь не найден"


class UserAlreadyExistsException(PeopleException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже сущетсвует"
