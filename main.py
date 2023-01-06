import logging
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from keyboards.inline_buttoms import inline_kb_login, inline_kb_admin
from dotenv import load_dotenv

from states.main import Main
from states.form import Form
from states.admin import Admin
from db.connection import connect
from init import bot, dp
from handlers.form import form_handler
from handlers.admin import admin_handler

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

async def send_welcome(message: types.Message):
    stri = ""
    for i in message.text.split():
        stri += i + " "
    if len(message.text.split()) == 1:
        await Main.login.set()
        await message.reply("Привет выберите действие ", reply_markup=inline_kb_login)
    else:
        await Form.start.set()
        # Init inline keyboard with buttons "Начать опрос" and callback data message.text.split()[1]
        inline_kb_client = types.InlineKeyboardMarkup()
        form_id = message.text.split()[1].split("form_")[1]
        inline_kb_client.add(types.InlineKeyboardButton(text="Начать опрос", callback_data="form_"+form_id))
        await message.reply("Привет выберите действие " + form_id, reply_markup=inline_kb_client)

@dp.callback_query_handler(lambda c: c.data == "login_admin", state=["Main:login", "Main:start"])
async def process_callback_button5(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    admins = []
    # Get admins from database
    connection, cursor = await connect()
    cursor.execute("SELECT * FROM admin;")
    for row in cursor:
        admins.append(row[1])

    username = callback_query.from_user.username
    if username not in admins:
        await bot.send_message(callback_query.from_user.id, "Вы не являетесь администратором")
        return
    await Admin.start.set()
    await bot.send_message(callback_query.from_user.id, "Вы вошли как админ", reply_markup=inline_kb_admin)

async def all_other_messages(message: types.Message):
    if message.text == "люблю путина":
        await message.reply("Ты не пидор, а блять пидорас")
        await bot.send_photo(message.from_user.id, "https://i.ytimg.com/vi/gjuVryYRGZE/maxresdefault.jpg")
    await message.reply("Кажется вы делаете что-то не то, попробуйте еще раз, или пропишите /start")

# Register handlers

def main_handler(dp):
    dp.register_callback_query_handler(process_callback_button5, lambda c: c.data == "login_admin", state=["Main:login", "Main:start"])


# Start long polling
if __name__ == '__main__':
    dp.register_message_handler(send_welcome, commands="start", state="*")
    # Register other handlers
    form_handler(dp)
    main_handler(dp)
    admin_handler(dp)
    dp.register_message_handler(all_other_messages, state="*")
    executor.start_polling(dp, skip_updates=True)

# Create tables in postgresql form table in postgresql with id (int, autoincrement), form path (text), form hash (text)
# CREATE TABLE forms (id SERIAL PRIMARY KEY, form_path text);
# CREATE TABLE admin (id SERIAL PRIMARY KEY, admin_id text);
# CREATE TABLE promos (id SERIAL PRIMARY KEY, promo text);