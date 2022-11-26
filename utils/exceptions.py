"""Кастомные исключения"""


class NotCorrectRefueling(Exception):
    """Некорректное сообщение в бот, которое не удалось распарсить"""
    pass


class NotCorrectCarName(Exception):
    """Некорректное имя автомобиля"""
    pass
