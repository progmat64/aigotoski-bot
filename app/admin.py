from aiogram import F, Router
from aiogram.filters import Command, CommandStart, Filter
from aiogram.types import CallbackQuery, Message

admin = Router()


# Список администраторов по tg_id
ADMINS = [7167447292]  # Укажите ваши Telegram ID


class Admin(Filter):
    """Фильтр для проверки прав администратора."""

    async def __call__(self, message: Message) -> bool:
        # Проверяем, находится ли tg_id пользователя в списке администраторов
        return message.from_user.id in ADMINS


@admin.message(Command("admin"), Admin())
async def cmd_admin(message: Message):
    """Обрабатывает команду /admin."""
    await message.answer("Добро пожаловать в панель администратора!")


from datetime import datetime

from app.database.requests import add_training


@admin.message(Command("add_training"))
async def add_training_handler(message: Message):
    """Добавляет новую тренировку."""
    try:
        args = message.text.split(maxsplit=1)[1]
        name, date_str, max_participants = args.split("|")
        date = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M")
        max_participants = int(max_participants.strip())

        await add_training(
            name=name.strip(), date=date, max_participants=max_participants
        )
        await message.answer(f"Тренировка '{name.strip()}' добавлена на {date}.")
    except (ValueError, IndexError):
        await message.answer(
            "Неправильный формат команды. Пример: /add_training Йога | 2025-01-20 18:00 | 10"
        )


from app.database.requests import edit_training


@admin.message(Command("edit_training"))
async def edit_training_handler(message: Message):
    """Редактирует тренировку по ID."""
    try:
        args = message.text.split(maxsplit=1)[1]
        training_id, updates = args.split("|", maxsplit=1)
        training_id = int(training_id.strip())

        name = date = max_participants = None
        for update in updates.split(";"):
            key, value = update.strip().split("=")
            if key == "name":
                name = value.strip()
            elif key == "date":
                date = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")
            elif key == "max":
                max_participants = int(value.strip())

        success = await edit_training(
            training_id, name=name, date=date, max_participants=max_participants
        )
        if success:
            await message.answer(f"Тренировка ID {training_id} успешно обновлена.")
        else:
            await message.answer(f"Тренировка с ID {training_id} не найдена.")
    except (ValueError, IndexError):
        await message.answer(
            "Неправильный формат команды. Пример: /edit_training 1 | name=Йога; date=2025-01-20 18:00; max=15"
        )


from app.database.requests import delete_training


@admin.message(Command("delete_training"))
async def delete_training_handler(message: Message):
    """Удаляет тренировку по ID."""
    try:
        training_id = int(message.text.split(maxsplit=1)[1])
        success = await delete_training(training_id)
        if success:
            await message.answer(f"Тренировка ID {training_id} успешно удалена.")
        else:
            await message.answer(f"Тренировка с ID {training_id} не найдена.")
    except (ValueError, IndexError):
        await message.answer(
            "Укажите корректный ID тренировки. Пример: /delete_training 1"
        )


from app.database.requests import get_user_bookings


@admin.message(Command("view_all_bookings"))
async def view_all_bookings_handler(message: Message):
    """Показывает администратору все записи."""
    bookings = await get_user_bookings(user_id=None)  # Получение всех записей
    if bookings:
        response = "\n".join(
            [
                f"{b.booking_id}: Пользователь {b.user.name or b.user.user_id}, Тренировка {b.training.name} ({b.training.date})"
                for b in bookings
            ]
        )
        await message.answer(f"Все записи:\n{response}")
    else:
        await message.answer("Записей пока нет.")


@admin.message(Command("help_admin"))
async def help_admin(message: Message):
    """Отображает список команд администратора."""
    commands = (
        "/add_training — добавление новой тренировки.\n"
        "/edit_training [id тренировки] — редактирование тренировки.\n"
        "/delete_training [id тренировки] — удаление тренировки.\n"
        "/view_all_bookings — просмотр всех записей пользователей.\n"
        "/help_admin — помощь по административным функциям."
    )
    await message.answer(f"Команды администратора:\n{commands}")
