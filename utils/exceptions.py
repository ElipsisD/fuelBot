"""Кастомные исключения"""


class NotCorrectRefueling(Exception):
    """Некорректное сообщение в бот, которое не удалось распарсить"""
    pass


class NotCorrectCarName(Exception):
    """Некорректное имя автомобиля"""
    pass


class NotEnoughRefuelings(Exception):
    """Недостаточное количество заправок"""
    pass


class NotCorrectData(Exception):
    """Некорректная дата"""
    pass


class NotCorrectNumber(Exception):
    """Некорректный пробег"""
    pass


class NotFoundMaintenance(Exception):
    """Данные о ТО отсутствуют"""
    pass
