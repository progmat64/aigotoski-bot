from datetime import datetime

from sqlalchemy import select

from app.database.models import Booking, Training, User, async_session


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def book_training(user_id: int, training_id: int):
    """Записывает пользователя на тренировку."""
    async with async_session() as session:
        # Проверка на существующую запись
        existing_booking = await session.scalar(
            select(Booking).where(
                Booking.user_id == user_id,
                Booking.training_id == training_id
            )
        )
        if existing_booking:
            return False, "Вы уже записаны на эту тренировку."

        # Проверка на доступные места
        training = await session.get(Training, training_id)
        if training and training.current_participants < training.max_participants:
            session.add(
                Booking(
                    user_id=user_id,
                    training_id=training_id,
                    booking_date=datetime.now(),
                    status=True,
                )
            )
            training.current_participants += 1
            await session.commit()
            return True, "Вы успешно записались на тренировку."
        return False, "Запись невозможна: тренировка недоступна или мест больше нет."



async def cancel_booking(user_id: int, training_id: int):
    """Удаляет запись пользователя на тренировку."""
    async with async_session() as session:
        booking = await session.scalar(
            select(Booking).where(
                Booking.user_id == user_id, Booking.training_id == training_id
            )
        )
        if booking:
            await session.delete(booking)
            training = await session.get(Training, training_id)
            if training:
                training.current_participants -= 1
            await session.commit()
            return True
        return False


async def get_user_bookings(user_id: int):
    """Получает список записей пользователя."""
    async with async_session() as session:
        bookings = await session.scalars(
            select(Booking).where(Booking.user_id == user_id)
        )
        return bookings.all()


async def get_trainings():
    """Получает список доступных тренировок из базы данных."""
    async with async_session() as session:
        result = await session.scalars(select(Training))
        return result.all()


async def add_training(name: str, date: datetime, max_participants: int):
    """Добавляет новую тренировку в базу данных."""
    async with async_session() as session:
        session.add(Training(name=name, date=date, max_participants=max_participants))
        await session.commit()


async def edit_training(
    training_id: int,
    name: str = None,
    date: datetime = None,
    max_participants: int = None,
):
    """Редактирует существующую тренировку."""
    async with async_session() as session:
        training = await session.get(Training, training_id)
        if not training:
            return False

        if name:
            training.name = name
        if date:
            training.date = date
        if max_participants:
            training.max_participants = max_participants

        await session.commit()
        return True


async def delete_training(training_id: int):
    """Удаляет тренировку из базы данных."""
    async with async_session() as session:
        training = await session.get(Training, training_id)
        if not training:
            return False
        await session.delete(training)
        await session.commit()
        return True


async def edit_booking(user_id: int, old_training_id: int, new_training_id: int):
    """Редактирует запись пользователя на новую тренировку."""
    async with async_session() as session:
        booking = await session.scalar(
            select(Booking).where(
                Booking.user_id == user_id, Booking.training_id == old_training_id
            )
        )
        if not booking:
            return False, "Старая запись не найдена."

        new_training = await session.get(Training, new_training_id)
        if not new_training:
            return False, "Выбранная новая тренировка не найдена."
        if new_training.current_participants >= new_training.max_participants:
            return False, "На выбранной тренировке больше нет мест."

        old_training = await session.get(Training, old_training_id)
        if old_training:
            old_training.current_participants -= 1

        new_training.current_participants += 1

        booking.training_id = new_training_id
        await session.commit()
        return True, "Запись успешно изменена."


from sqlalchemy.orm import joinedload

async def get_user_bookings(user_id: int = None):
    """Получает список записей на тренировки.
    Если `user_id` не указан, возвращает записи для всех пользователей.
    """
    async with async_session() as session:
        query = (
            select(Booking)
            .options(
                joinedload(Booking.training),
                joinedload(Booking.user),
            )
        )
        if user_id:
            query = query.where(Booking.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().all()
