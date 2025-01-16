from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database.models import Booking, Training, User, async_session


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def book_training(user_id, training_id):
    async with async_session() as session:
        if await session.scalar(
            select(Booking).where(
                Booking.user_id == user_id, Booking.training_id == training_id
            )
        ):
            return False, "Вы уже записаны на эту тренировку."

        training = await session.get(Training, training_id)
        if (
            training
            and training.current_participants < training.max_participants
        ):
            session.add(
                Booking(
                    user_id=user_id,
                    training_id=training_id,
                    booking_date=datetime.now(),
                    status=True,
                )
            )
            training.current_participants += 1
            training_name = training.name
            training_date = training.date
            await session.commit()
            return (
                True,
                f"Вы успешно записались на тренировку {training_name} в {training_date}. ",
            )

        return (
            False,
            "Запись невозможна: тренировка недоступна или мест больше нет.",
        )


async def cancel_booking(user_id, booking_id):
    async with async_session() as session:
        try:
            booking = await session.get(Booking, booking_id)
            if booking and booking.user_id == user_id:
                await session.delete(booking)

                training = await session.get(Training, booking.training_id)
                if training:
                    training.current_participants -= 1

                await session.commit()
                return True
            return False
        except Exception as e:
            await session.rollback()
            print(f"Error during cancel_booking: {e}")
            return False


async def get_user_bookings(user_id):
    async with async_session() as session:
        bookings = await session.scalars(
            select(Booking).where(Booking.user_id == user_id)
        )
        return bookings.all()


async def get_trainings():
    async with async_session() as session:
        return (await session.scalars(select(Training))).all()


async def add_training(name, date, max_participants):
    async with async_session() as session:
        session.add(
            Training(name=name, date=date, max_participants=max_participants)
        )
        await session.commit()


async def edit_training(
    training_id, name=None, date=None, max_participants=None
):
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


async def delete_training(training_id):
    async with async_session() as session:
        training = await session.get(Training, training_id)
        if not training:
            return False
        await session.delete(training)
        await session.commit()
        return True


async def get_user_bookings(user_id=None):
    async with async_session() as session:
        query = select(Booking).options(
            joinedload(Booking.training), joinedload(Booking.user)
        )
        if user_id:
            query = query.where(Booking.user_id == user_id)
        return (await session.execute(query)).scalars().all()
