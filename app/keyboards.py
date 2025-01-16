from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/add_training")],
        [KeyboardButton(text="/edit_training")],
        [KeyboardButton(text="/delete_training")],
        [KeyboardButton(text="/view_all_bookings")],
        [KeyboardButton(text="/help_admin")],
    ],
    resize_keyboard=True,
)

user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💪 Записаться на тренировку"),
            KeyboardButton(text="😥 Отменить тренировку"),
        ],
        [
            KeyboardButton(text="⚡ Советы и стратегии"),
            KeyboardButton(text="🗣 Пообщаться с тренером"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    row_width=2,
)


def schedule_keyboard(trainings):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{t.name} ({t.date})",
                    callback_data=f"book_{t.training_id}",
                )
            ]
            for t in trainings
        ]
    )


def bookings_keyboard(bookings):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Отменить {b.training.name}",
                    callback_data=f"cancel_{b.booking_id}",
                )
            ]
            for b in bookings
        ]
    )
