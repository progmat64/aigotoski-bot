from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.requests import (book_training, cancel_booking, edit_booking,
                                   get_trainings, get_user_bookings, set_user)
from app.generators import generate
from app.states import Work

user = Router()


@user.message(CommandStart())
async def register_user(message: Message):
    """Регистрирует пользователя при первом запуске бота."""
    await set_user(message.from_user.id)
    await message.answer(
        "Привет! Я твой персональный AI-тренер! Используйте /help для получения списка команд."
    )


@user.message(Work.process)
async def stop(message: Message):
    await message.answer("Подождите, ваше сообщение генерируется...")


@user.message(Command("view_schedule"))
async def view_schedule(message: Message):
    """Показывает пользователю доступные тренировки."""
    trainings = await get_trainings()
    if trainings:
        response = "\n".join(
            [f"{t.training_id}: {t.name} ({t.date})" for t in trainings]
        )
        await message.answer(f"Доступные тренировки:\n{response}")
    else:
        await message.answer("Тренировок пока нет.")


from aiogram.filters.command import CommandObject



@user.message(Command("book"))
async def book(message: Message, command: CommandObject):
    """Обрабатывает запись пользователя на тренировку."""
    args = command.args
    if not args:
        await message.answer("Укажите ID тренировки. Пример: /book 1")
        return

    try:
        training_id = int(args)
        success, response = await book_training(
            user_id=message.from_user.id, training_id=training_id
        )
        await message.answer(response)
    except ValueError:
        await message.answer("Укажите корректный ID тренировки. Пример: /book 1")



@user.message(Command("cancel"))
async def cancel(message: Message, command: CommandObject):
    """Удаляет запись пользователя на тренировку."""
    args = command.args
    if not args:
        await message.answer("Укажите ID тренировки. Пример: /cancel 1")
        return

    try:
        training_id = int(args)
        success = await cancel_booking(
            user_id=message.from_user.id, training_id=training_id
        )
        if success:
            await message.answer(
                f"Вы успешно удалили запись на тренировку ID {training_id}."
            )
        else:
            await message.answer("Вы не записаны на эту тренировку.")
    except ValueError:
        await message.answer("Укажите корректный ID тренировки. Пример: /cancel 1")


@user.message(Command("my_bookings"))
async def my_bookings_handler(message: Message):
    """Показывает записи пользователя на тренировки."""
    bookings = await get_user_bookings(user_id=message.from_user.id)
    if bookings:
        response = "\n\n".join(
            [
                f"Запись ID: {booking.booking_id}\n"
                f"Тренировка: {booking.training.name}\n"
                f"Дата и время: {booking.training.date.strftime('%Y-%m-%d %H:%M')}\n"
                f"Статус: {'Активна' if booking.status else 'Отменена'}"
                for booking in bookings
            ]
        )
        await message.answer(f"Ваши записи:\n\n{response}")
    else:
        await message.answer("У вас пока нет записей на тренировки.")


@user.message(Command("edit"))
async def edit_booking_handler(message: Message):
    """Обрабатывает редактирование записи пользователя."""
    args = message.text.split(maxsplit=1)[1:]
    if len(args) != 2:
        await message.answer("Укажите ID старой и новой тренировки. Пример: /edit 1 2")
        return

    try:
        old_training_id, new_training_id = map(int, args[0].split())
        success, response = await edit_booking(
            user_id=message.from_user.id,
            old_training_id=old_training_id,
            new_training_id=new_training_id,
        )
        await message.answer(response)
    except ValueError:
        await message.answer("Укажите корректные ID тренировок. Пример: /edit 1 2")


@user.message(Command("help"))
async def help_command(message: Message):
    """Отображает список доступных команд для пользователя."""
    commands = (
        "/start — регистрация пользователя.\n"
        "/view_schedule — просмотр доступных тренировок.\n"
        "/my_bookings — просмотр всех записей пользователя.\n"
        "/book [id тренировки] — запись на тренировку.\n"
        "/cancel [id тренировки] — удаление записи на тренировку.\n"
        "/edit [старый id] [новый id] — редактирование записи на тренировку.\n"
        "/help — помощь по работе с ботом."
    )
    await message.answer(f"Доступные команды:\n{commands}")


#######################


@user.message()
async def ai(message: Message, state: FSMContext):
    await state.set_state(Work.process)
    res = await generate(message.text)
    await message.answer(res.choices[0].message.content)
    await state.clear()
