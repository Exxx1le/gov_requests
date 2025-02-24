from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from pathlib import Path
from aiogram.types import FSInputFile

from config import TELEGRAM_BOT_KEY
from main import main


bot = Bot(token=TELEGRAM_BOT_KEY)
dp = Dispatcher()


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer(
        "Привет!\nЯ бот, который поможет поможет тебе выгрузить информацию о документах с портала publication.pravo.gov.ru"
    )


@dp.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    await message.answer("Запустите команду /get_documents и введите даты в формате YYYY-MM-DD")


class DateInput(StatesGroup):
    waiting_for_start_date = State()
    waiting_for_end_date = State()

@dp.message(Command(commands=["get_documents"]))
async def start_date_input(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите начальную дату в формате YYYY-MM-DD")
    await state.set_state(DateInput.waiting_for_start_date)

@dp.message(DateInput.waiting_for_start_date)
async def process_start_date(message: Message, state: FSMContext):
    try:
        start_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        await state.update_data(start_date=start_date)
        await message.answer("Теперь введите конечную дату в формате YYYY-MM-DD")
        await state.set_state(DateInput.waiting_for_end_date)
    except ValueError:
        await message.answer("Неверный формат даты. Используйте формат YYYY-MM-DD")

@dp.message(DateInput.waiting_for_end_date)
async def process_end_date(message: Message, state: FSMContext):
    try:
        end_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        data = await state.get_data()
        start_date = data['start_date']
        
        if start_date > end_date:
            await message.answer("Начальная дата не может быть позже конечной даты")
            return
            
        await message.answer("Начинаю поиск документов...")
        main(start_date, end_date)
        
        # Отправляем файл пользователю
        doc_path = str(Path.home() / "output_documents.docx")
        await message.answer_document(FSInputFile(doc_path))
        await state.clear()
        
    except ValueError:
        await message.answer("Неверный формат даты. Используйте формат YYYY-MM-DD")



@dp.message(F.content_type != "text")
async def send_other(message: Message):
    await message.answer("К сожалению, я могу распознавать только даты 😢")


if __name__ == "__main__":
    dp.run_polling(bot)