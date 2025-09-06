from aiogram import types, Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup

from database import get_quiz_index, update_quiz_index, get_rating, get_stats
from questions import quiz_data

router = Router()

kb_main = ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text='Начать игру')],
    [types.KeyboardButton(text='Просмотр статистики')],

],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Веберите пункт меню...'
)

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question(message, user_id: int):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    count_right_answer = 0
    await update_quiz_index(user_id, current_question_index, count_right_answer)
    await get_question(message, user_id)


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1

    rating = await get_rating(callback.from_user.id)
    # Обновление счетчика правильных ответов
    if rating is None:
        rating=0
    rating += 1

    await update_quiz_index(callback.from_user.id, current_question_index, rating)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    rating = await get_rating(callback.from_user.id)
    await update_quiz_index(callback.from_user.id, current_question_index, rating)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в квиз!", reply_markup=kb_main)


# Хэндлер на команду /quiz
@router.message(F.text.lower()=="начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


# Хэндлер на команду /stats
@router.message(F.text.lower()=="просмотр статистики")
@router.message(Command("stats"))
async def cmd_quiz(message: types.Message):
    user_id = message.from_user.id
    stats = await get_stats(user_id)
    await message.answer(stats, parse_mode="Markdown")
