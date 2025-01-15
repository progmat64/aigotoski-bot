from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from app.database.requests import set_user
# from middlewares import BaseMiddleware

from app.generators import generate
from app.states import Work


user = Router()

# user.message.middleware(BaseMiddleware())

@user.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)
    await message.answer('Добро пожаловать в бот!')


@user.message(Work.process)
async def stop(message: Message):
    await message.answer('Подождите, ваше сообщение генерируется...')


@user.message()
async def ai(message: Message, state: FSMContext):
    await state.set_state(Work.process)
    res = await generate(message.text)
    await message.answer(res.choices[0].message.content)
    await state.clear()