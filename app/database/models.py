from datetime import datetime  # Импорт стандартного Python типа

from sqlalchemy import (BigInteger, Boolean, DateTime, ForeignKey, Integer,
                        String)
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import DB_URL

# Создание асинхронного движка для базы данных
engine = create_async_engine(url=DB_URL, echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей."""

    pass


# Таблица пользователей
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )  # Автоинкремент
    tg_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )  # ID Telegram пользователя
    name: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Имя пользователя (опционально)
    contact_info: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Контактная информация (опционально)

    # Связь с таблицей записей
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")


# Таблица тренировок
class Training(Base):
    __tablename__ = "trainings"

    training_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )  # Уникальный ID тренировки
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Название тренировки
    date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )  # Дата и время тренировки (Python тип datetime)
    max_participants: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # Максимальное количество участников
    current_participants: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Текущее количество участников

    # Связь с таблицей записей
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="training"
    )


# Таблица записей
class Booking(Base):
    __tablename__ = "bookings"

    booking_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )  # Уникальный ID записи
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"), nullable=False
    )  # ID пользователя (FK)
    training_id: Mapped[int] = mapped_column(
        ForeignKey("trainings.training_id"), nullable=False
    )  # ID тренировки (FK)
    booking_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )  # Дата и время записи (Python тип datetime)
    status: Mapped[bool] = mapped_column(
        Boolean, default=True
    )  # Статус записи (активна/отменена)

    # Обратные связи
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    training: Mapped["Training"] = relationship("Training", back_populates="bookings")


# Функция для создания таблиц в базе данных
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
