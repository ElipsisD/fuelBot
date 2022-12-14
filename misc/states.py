from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMNewRefueling(StatesGroup):
    adding_car = State()
    choice_of_car = State()
    data = State()


class FSMActions(StatesGroup):
    new_car_name = State()