from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.requests import (book_training, cancel_booking,
                                   get_trainings, get_user_bookings, set_user)
from app.generators import generate
from app.states import Work

user = Router()


@user.message(CommandStart())
async def register_user(message: Message):
    await set_user(message.from_user.id)
    await message.answer("Привет! Я твой персональный AI-тренер! Используйте /help для получения списка команд.")


@user.message(Work.process)
async def stop(message: Message):
    await message.answer("Подождите, ваше сообщение генерируется...")


@user.message(Command("view_schedule"))
async def view_schedule(message: Message):
    trainings = await get_trainings()
    if trainings:
        response = "\n".join([f"{t.training_id}: {t.name} ({t.date})" for t in trainings])
        await message.answer(f"Доступные тренировки:\n{response}")
    else:
        await message.answer("Тренировок пока нет.")


@user.message(Command("book"))
async def book(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Укажите ID тренировки. Пример: /book 1")
        return
    try:
        training_id = int(command.args)
        success, response = await book_training(user_id=message.from_user.id, training_id=training_id)
        await message.answer(response)
    except ValueError:
        await message.answer("Укажите корректный ID тренировки. Пример: /book 1")


@user.message(Command("cancel"))
async def cancel(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Укажите ID тренировки. Пример: /cancel 1")
        return
    try:
        training_id = int(command.args)
        success = await cancel_booking(user_id=message.from_user.id, training_id=training_id)
        await message.answer(
            f"Вы успешно удалили запись на тренировку ID {training_id}."
            if success
            else "Вы не записаны на эту тренировку."
        )
    except ValueError:
        await message.answer("Укажите корректный ID тренировки. Пример: /cancel 1")


@user.message(Command("my_bookings"))
async def my_bookings_handler(message: Message):
    bookings = await get_user_bookings(user_id=message.from_user.id)
    if bookings:
        response = "\n\n".join(
            [
                f"Запись ID: {booking.booking_id}\nТренировка: {booking.training.name}\n"
                f"Дата и время: {booking.training.date.strftime('%Y-%m-%d %H:%M')}\nСтатус: {'Активна' if booking.status else 'Отменена'}"
                for booking in bookings
            ]
        )
        await message.answer(f"Ваши записи:\n\n{response}")
    else:
        await message.answer("У вас пока нет записей на тренировки.")


@user.message(Command("help"))
async def help_command(message: Message):
    commands = (
        "/start — регистрация пользователя.\n"
        "/view_schedule — просмотр доступных тренировок.\n"
        "/my_bookings — просмотр всех записей пользователя.\n"
        "/book [id тренировки] — запись на тренировку.\n"
        "/cancel [id тренировки] — удаление записи на тренировку.\n"
        "/help — помощь по работе с ботом."
    )
    await message.answer(f"Доступные команды:\n{commands}")


@user.message()
async def ai(message: Message, state: FSMContext):
    await state.set_state(Work.process)
    response = await generate(message.text)
    await message.answer(response.choices[0].message.content)
    await state.clear()
