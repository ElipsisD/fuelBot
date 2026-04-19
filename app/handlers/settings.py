import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.handlers.common import edit_callback_message, edit_message, prompt_for_state, state_data
from app.keyboards.menu_bot import menu, back_key
from app.keyboards.settings import SettingsCallback, settings_menu
from app.misc.states import FSMSettings
from app.db import set_service_interval
from app.utils import exceptions, maintenance_info, refuelings

logger = logging.getLogger('telegram_logger')
router = Router(name="settings")


@router.callback_query(F.data == 'settings')
async def choice_setting(call: CallbackQuery):
    """Выбор настройки"""
    await edit_callback_message(call, "Что нужно настроить?", settings_menu())


@router.callback_query(SettingsCallback.filter(F.mode == 'interval'))
async def change_interval(call: CallbackQuery, state: FSMContext):
    """Реакция на кнопку ИЗМЕНИТЬ ИНТЕРВАЛ"""
    await prompt_for_state(
        call,
        state,
        FSMSettings.new_service_interval,
        'Введите желаемый интервал сервисного обслуживания',
        back_key,
        prev_m=call.message,
    )


@router.message(FSMSettings.new_service_interval)
async def new_interval(m: Message, state: FSMContext):
    """Валидация нового интервала и запись в БД"""
    context_data = await state_data(state)
    prev_m = context_data['prev_m']
    try:
        new_inter = maintenance_info.parse_maintenance_number(m.text)
        set_service_interval(str(m.from_user.id), new_inter)
        await edit_message(
            prev_m,
            f'✅ Изменения прошли успешно\nинтервал сервисного обслуживания: {new_inter} км',
            menu,
        )
        logger.info(f'{m.from_user.first_name} изменил интервал сервисного обслуживания: {new_inter}')
        await m.delete()
        await state.clear()
    except exceptions.NotCorrectNumber as e:
        await m.delete()
        await edit_message(prev_m, str(e), back_key)


@router.callback_query(SettingsCallback.filter(F.mode == 'change_last_ref'))
async def change_last_refueling(call: CallbackQuery, state: FSMContext):
    """Реакция на кнопку ИЗМЕНИТЬ ПОСЛЕДНИЕ ДАННЫЕ О ЗАПРАВКЕ"""
    answer, full_ref_mode = refuelings.last_refueling_data(str(call.from_user.id))
    await prompt_for_state(
        call,
        state,
        FSMSettings.change_last_refueling,
        answer,
        back_key,
        prev_m=call.message,
        full_ref_mode=full_ref_mode,
    )


@router.message(FSMSettings.change_last_refueling)
async def change_data_handler(m: Message, state: FSMContext):
    """Парсинг данных для изменения последней заправки"""
    context_data = await state_data(state)
    prev_m = context_data['prev_m']
    full_ref_mode = context_data['full_ref_mode']
    try:
        user_id = str(m.from_user.id)
        refuelings.change_last_refueling(user_id, m.text, full_ref_mode)
        logger.info(f'{m.from_user.first_name} изменил данные о последней заправке')
        await edit_message(prev_m, "✅ Изменения прошли успешно", menu)
        await m.delete()
        await state.clear()
    except (exceptions.NotCorrectRefueling, exceptions.NotEnoughRefuelings) as e:
        await m.delete()
        await edit_message(prev_m, str(e), back_key)
