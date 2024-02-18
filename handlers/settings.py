"""Работа с меню Настройки"""
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards.menu_bot import menu, back_key
from keyboards.settings import settings_menu, settings_menu_cb
from misc.states import FSMSettings
from utils import db, exceptions, maintenance_info, refuelings

logger = logging.getLogger('telegram_logger')


async def choice_setting(call: types.CallbackQuery):
    """Выбор настройки"""
    await call.message.edit_text("Что нужно настроить?")
    await call.message.edit_reply_markup(reply_markup=settings_menu())


async def change_interval(call: types.CallbackQuery, state: FSMContext):
    """Реакция на кнопку ИЗМЕНИТЬ ИНТЕРВАЛ"""
    await FSMSettings.new_service_interval.set()
    async with state.proxy() as context_data:
        context_data['prev_m'] = call.message
    await call.message.edit_text('Введите желаемый интервал сервисного обслуживания')
    await call.message.edit_reply_markup(reply_markup=back_key)


async def new_interval(m: types.Message, state: FSMContext):
    """Валидация нового интервала и запись в БД"""
    async with state.proxy() as context_data:
        prev_m = context_data['prev_m']
    try:
        new_inter = maintenance_info.parse_maintenance_number(m.text)
        db.set_service_interval(str(m.from_user.id), new_inter)
        await prev_m.edit_text(f'✅ Изменения прошли успешно\nинтервал сервисного обслуживания: {new_inter} км')
        await prev_m.edit_reply_markup(reply_markup=menu)
        logger.info(f'{m.from_user.first_name} изменил интервал сервисного обслуживания: {new_inter}')
        await m.delete()
        await state.finish()
    except exceptions.NotCorrectNumber as e:
        await m.delete()
        await prev_m.edit_text(str(e))
        await prev_m.edit_reply_markup(reply_markup=back_key)


async def change_last_refueling(call: types.CallbackQuery, state: FSMContext):
    """Реакция на кнопку ИЗМЕНИТЬ ПОСЛЕДНИЕ ДАННЫЕ О ЗАПРАВКЕ"""
    await FSMSettings.change_last_refueling.set()
    answer, full_ref_mode = refuelings.last_refueling_data(str(call.from_user.id))
    async with state.proxy() as context_data:
        context_data['prev_m'] = call.message
        context_data['full_ref_mode'] = full_ref_mode
    await call.message.edit_text(answer)
    await call.message.edit_reply_markup(reply_markup=back_key)


async def change_data_handler(m: types.Message, state: FSMContext):
    """Парсинг данных для изменения последней заправки"""
    async with state.proxy() as context_data:
        prev_m = context_data['prev_m']
        full_ref_mode = context_data['full_ref_mode']
    try:
        user_id = str(m.from_user.id)
        refuelings.change_last_refueling(user_id, m.text, full_ref_mode)
        logger.info(f'{m.from_user.first_name} изменил данные о последней заправке')
        await prev_m.edit_text("✅ Изменения прошли успешно", reply_markup=menu)
        await m.delete()
        await state.finish()
    except (exceptions.NotCorrectRefueling, exceptions.NotEnoughRefuelings) as e:
        await m.delete()
        await prev_m.edit_text(str(e))
        await prev_m.edit_reply_markup(reply_markup=back_key)


def register_user_settings(dp: Dispatcher):
    """Регистрация хендлеров"""
    dp.register_callback_query_handler(choice_setting, text='settings')
    dp.register_callback_query_handler(change_interval, settings_menu_cb.filter(mode='interval'))
    dp.register_message_handler(new_interval, state=FSMSettings.new_service_interval)
    dp.register_callback_query_handler(change_last_refueling, settings_menu_cb.filter(mode='change_last_ref'))
    dp.register_message_handler(change_data_handler, state=FSMSettings.change_last_refueling)
