
class ConnectionError(Exception):
    """Ошибка соединения с API расписания"""


class GroupDoesNotExist(Exception):
    """Группы не существует"""


class ParameterError(Exception):
    """Неправильные параметры в теле запроса"""