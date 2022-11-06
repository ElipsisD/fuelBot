"""Работа с БД"""
import json

filename = 'db.json'


def set_new_data(new_data: dict) -> None:
    """Добавление нового объекта в БД"""
    data = get_data()
    with open(filename, 'r+', encoding='utf8') as f:
        data.append(new_data)
        json.dump(data, f, ensure_ascii=False)


def get_data() -> list:
    """Получение всей БД"""
    with open(filename, 'r', encoding='utf8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def get_user_data(user_id) -> list:
    """Возвращает объект БД, связанный с пользователем
    и удаляет его из БД"""
    for obj in get_data():
        if obj['user_id'] == user_id:
            pass

    with open(filename, 'r', encoding='utf8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []