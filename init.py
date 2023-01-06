import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Configure bot and dispatcher
storage = MemoryStorage()

API_TOKEN = os.environ.get("API_TOKEN")
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)