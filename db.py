"""Работа с БД"""
import json

filename = 'db.json'


def set_data(new_data: dict) -> None:
    data = get_data()
    with open(filename, 'r+', encoding='utf8') as f:
        data.append(new_data)
        json.dump(data, f, ensure_ascii=False)


def get_data() -> list:
    with open(filename, 'r', encoding='utf8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
