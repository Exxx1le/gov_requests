import os
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, BotCommandScopeDefault, CallbackQuery, FSInputFile, Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config import TELEGRAM_BOT_KEY
from utils import process_documents

bot = Bot(token=TELEGRAM_BOT_KEY)
dp = Dispatcher()


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer(
        "Привет!\nЯ бот, который поможет тебе выгрузить информацию о документах с портала publication.pravo.gov.ru"
    )


@dp.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    await message.answer("Запустите команду /get_documents для выбора дат")


class DateInput(StatesGroup):
    waiting_for_dates = State()


@dp.message(Command(commands=["get_documents"]))
async def start_date_input(message: Message, state: FSMContext):
    await state.set_state(DateInput.waiting_for_dates)
    calendar = SimpleCalendar()
    await message.answer(
        "Пожалуйста, выберите начальную и конечную дату:", reply_markup=await calendar.start_calendar()
    )


@dp.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback_query, callback_data)

    if selected:
        data = await state.get_data()

        if "start_date" not in data:
            await state.update_data(start_date=date)
            await callback_query.message.answer(
                f"Начальная дата: {date.strftime('%Y-%m-%d')}\n" f"Теперь выберите конечную дату:",
                reply_markup=await calendar.start_calendar(),
            )
        else:
            start_date = data["start_date"]
            if date < start_date:
                await callback_query.message.answer(
                    "Конечная дата не может быть раньше начальной. Пожалуйста, выберите другую дату:",
                    reply_markup=await calendar.start_calendar(),
                )
                return

            await callback_query.message.answer("Начинаю поиск документов...")
            process_documents(start_date, date)

            doc_path = str(Path.home() / "output_documents.docx")
            try:
                await callback_query.message.answer_document(FSInputFile(doc_path))
                os.remove(doc_path)
            except Exception as e:
                await callback_query.message.answer(f"Произошла ошибка при обработке файла: {str(e)}")
            finally:
                if os.path.exists(doc_path):
                    os.remove(doc_path)
                await state.clear()


@dp.message(F.content_type != "text")
async def send_other(message: Message):
    await message.answer("К сожалению, я могу работать только с выбором дат через календарь 😢")


# Создаем список команд для меню
async def set_commands():
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Получить справку"),
        BotCommand(command="get_documents", description="Выбрать даты и получить документы"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


# Добавляем инициализацию команд при запуске бота
async def start_bot():
    await set_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_bot())
