from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.keyboards.menu_bot import menu


async def edit_message(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    await message.edit_text(text)
    await message.edit_reply_markup(reply_markup=reply_markup)


async def edit_callback_message(
    call: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    await edit_message(call.message, text, reply_markup)
    await call.answer()


async def prompt_for_state(
    call: CallbackQuery,
    state: FSMContext,
    next_state: Any,
    text: str,
    reply_markup: InlineKeyboardMarkup | None,
    **data: Any,
) -> None:
    await state.set_state(next_state)
    await state.update_data(**data)
    await edit_callback_message(call, text, reply_markup)


async def state_data(state: FSMContext) -> dict[str, Any]:
    return await state.get_data()


async def delete_message(message: Message) -> None:
    await message.delete()


async def answer_with_main_menu(message: Message, first_name: str) -> None:
    await message.answer(f"⬇<b>{first_name}</b>, выбирай⬇", reply_markup=menu)
