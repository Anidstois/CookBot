from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from token_data import BOT_TOKEN
from recipes_handler import register_handlers


# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# Обработчик команды /start
@dp.message_handler(commands="start")
async def start_command(message: types.Message):
    await message.answer(
        "Добро пожаловать в бот рецептов! Вот доступные команды:\n"
        "/category_search_random <число> - Выбрать категорию и случайные рецепты"
    )

# Регистрация обработчиков
register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
