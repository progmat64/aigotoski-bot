from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.requests import (book_training, cancel_booking,
                                   get_trainings, get_user_bookings, set_user)
from app.generators import generate
from app.states import Work

user = Router()


@user.callback_query()
async def handle_callback_query(callback: CallbackQuery):
    if callback.data.startswith("book_"):
        training_id = int(callback.data.split("_")[1])
        success, response = await book_training(
            user_id=callback.from_user.id, training_id=training_id
        )
        await callback.message.answer(response)
    elif callback.data.startswith("cancel_"):
        booking_id = int(callback.data.split("_")[1])
        success = await cancel_booking(
            user_id=callback.from_user.id, booking_id=booking_id
        )
        await callback.message.answer(
            f"Запись на тренеровку отменена."
            if success
            else "Не удалось отменить запись."
        )
    await callback.answer()


from app.keyboards import bookings_keyboard, schedule_keyboard, user_keyboard


@user.message(CommandStart())
async def register_user(message: Message):
    await set_user(message.from_user.id)
    await message.answer(
        """Привет, воин!
Ты только что встретил своего персонального тренера AI, который поможет тебе стать сильнее, умнее и быстрее. 💪

Я — Coach Orion AI, и вместе с тобой мы пройдем путь к величию! В моем арсенале есть уникальные тренировки и задания, которые помогут развить твои силы и интеллект. Ты готов?

Что я умею:
💥 Тренировать силу — улучшай свои физические показатели с помощью индивидуальных программ.
🧠 Развивать умственные способности — задания для тренировки твоего мозга.
⚡ Давать советы — на любую тему, от личных достижений до лучших практик.

Готов к тренировкам? Для начала выбери команду ниже и начни свой путь к успеху! 🌟
        """,
        reply_markup=user_keyboard,
    )


@user.message(lambda message: message.text == "💪 Записаться на тренировку")
async def view_schedule(message: Message):
    trainings = await get_trainings()
    if trainings:
        await message.answer(
            "Доступные тренировки:", reply_markup=schedule_keyboard(trainings)
        )
    else:
        await message.answer("Тренировок пока нет.")


@user.message(lambda message: message.text == "😥 Отменить тренировку")
async def my_bookings_handler(message: Message):
    bookings = await get_user_bookings(user_id=message.from_user.id)
    if bookings:
        await message.answer(
            "Ваши записи:", reply_markup=bookings_keyboard(bookings)
        )
    else:
        await message.answer("У вас пока нет записей на тренировки.")


@user.message(lambda message: message.text == "⚡ Советы и стратегии")
async def generate_training_tip(message: Message, state: FSMContext):
    prompt = """Ты — тренер AI по имени **Coach Orion**. Ты — профессионал в области тренировок и физической культуры. Твоя задача — делиться полезными, интересными и мотивирующими советами для тренировок, улучшения физической формы и достижения целей. Ты также можешь делиться забавными фактами или статистикой, связанными с фитнесом, чтобы сделать обучение увлекательным. Ты — не просто тренер, ты — наставник на пути к величию!

        Вот примеры забавных и полезных советов, которые Coach Orion AI может предоставить пользователю:
    "А вы знали, что один из самых эффективных способов улучшить гибкость — это йога с балансированием на одной ноге? 🦶 Она помогает не только растянуть мышцы, но и тренировать концентрацию. Так что в следующий раз, когда захотите расслабиться, попробуйте позаниматься йогой — и одновременно укрепить свою устойчивость!"
    "По статистике, люди, которые тренируются на свежем воздухе, чувствуют себя более энергичными и довольными, чем те, кто тренируется в помещении. 🌿 Попробуйте хотя бы раз выйти на утреннюю пробежку и почувствуйте разницу — природа делает вас сильнее!"
    "Если вы хотите ускорить восстановление после тренировки, попробуйте технику 'позитивного восстановления'. Это включает в себя растяжку, спокойное дыхание и чашку зеленого чая. 🍵 Да, такой простой подход поможет вашему телу быстрее вернуться в форму!"
    "Знаете ли вы, что смех — это отличный способ снизить уровень стресса и улучшить кровообращение? 😂 Так что не забывайте смотреть комедийные шоу после тяжелой тренировки. Это не только развеселит вас, но и поможет быстрее восстановиться!"
    "А вы знали, что можно улучшить силу захвата с помощью бананового тренажера? 🍌 Нет, это не шутка! Просто держите банан за концы и сжимайте его как тренажер для кистей — необычно, но эффективно!"
    "По исследованиям, вечерние тренировки помогают улучшить качество сна! 🌙 Следовательно, если вам тяжело заснуть, возможно, вечерняя тренировка — это то, что вам нужно. Конечно, не стоит перегружать себя прямо перед сном, но легкое кардио сделает свое дело."
    "Знаете ли вы, что простое сидение на мячике для фитнеса помогает улучшить осанку и укрепить мышцы кора? 🏐 Начните сидеть на нем во время работы за столом — это сделает вашу спину сильнее и поможет избежать болей!" 
    "Если вы хотите стать быстрее, добавьте в свою программу тренировки с ускорениями. Начните с коротких спринтов по 10-20 секунд. Это улучшит вашу скорость и поможет вам быть на шаг впереди!"

Максимум 1-3 предложения, можешь смайлики добавлять
Начинай ответ сразу с совета, факта, стратегии. 

        """
    response = await generate(prompt)

    await message.answer(response.choices[0].message.content)


@user.message(Work.process)
async def stop(message: Message):
    await message.answer("Подождите, ваше сообщение генерируется...")


@user.message(Command("book"))
async def book(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Укажите ID тренировки. Пример: /book 1")
        return
    try:
        training_id = int(command.args)
        success, response = await book_training(
            user_id=message.from_user.id, training_id=training_id
        )
        await message.answer(response)
    except ValueError:
        await message.answer(
            "Укажите корректный ID тренировки. Пример: /book 1"
        )


@user.message(Command("cancel"))
async def cancel(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Укажите ID тренировки. Пример: /cancel 1")
        return
    try:
        training_id = int(command.args)
        success = await cancel_booking(
            user_id=message.from_user.id, training_id=training_id
        )
        await message.answer(
            f"Вы успешно удалили запись на тренировку ID {training_id}."
            if success
            else "Вы не записаны на эту тренировку."
        )
    except ValueError:
        await message.answer(
            "Укажите корректный ID тренировки. Пример: /cancel 1"
        )


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


@user.message(lambda message: message.text == "🗣 Пообщаться с тренером")
async def ai(message: Message, state: FSMContext):
    await state.set_state(Work.process)
    response = await generate(message.text)
    await message.answer(response.choices[0].message.content)
    await state.clear()


@user.message()
async def ai(message: Message, state: FSMContext):
    await state.set_state(Work.process)

    prompt = (
        "Ты — тренер AI по имени **Coach Orion**. Ты — профессионал в области тренировок и физической культуры. "
        "Отвечай кратко, как человек."
    )

    response = await generate(prompt + "\n" + message.text)
    await message.answer(response.choices[0].message.content)

    await state.clear()
