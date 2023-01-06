from aiogram import types
from aiogram.dispatcher import FSMContext
from states.form import Form
from db.connection import connect
from init import bot
import csv
import random

async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # Read from cvs file and create a list of values
    # Get from file_id from callback data and fined in database
    connection, cursor = await connect()
    cursor.execute("SELECT * FROM forms WHERE id = %s", (callback_query.data.split("_")[1],))
    record = cursor.fetchone()
    with open(record[1], 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    i = 1
    await state.update_data(i=i)
    await state.update_data(record=record[1])
    print(data)
    inline_kb_form = types.InlineKeyboardMarkup()
    inline_kb_form.add(types.InlineKeyboardButton(text="Начать", callback_data="active_"))
    await bot.send_message(callback_query.from_user.id, data[0][3], reply_markup=inline_kb_form)

async def process_callback_button2(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # Write to state data from callback query
    print(callback_query.data)
    record = await state.get_data()
    record = record["record"]
    with open(record, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    n = len(data[1])
    i = await state.get_data()
    i = i["i"]
    await state.update_data(i=i+1)
    print(i)
    if i == 1:
        await state.update_data(answers=[])
    else:
        # get data from state and uppend to list
        datas = await state.get_data()
        # Get answers from state and read from csv file
        answ = callback_query.data.split("_")[1]
        # Get from data list of answers an dget answ with index answer
        arr = []
        print(answ)
        for j in answ.split(","):
            arr.append(data[3][i-1].split(",")[int(j)-1])
        datas["answers"].append(arr)
        await state.update_data(answers=datas["answers"])
    inline_kb_form = types.InlineKeyboardMarkup()  
    if i > n-1:
        inline_kb_form.add(types.InlineKeyboardButton(text="Завершить", callback_data="endForm_"))
        await bot.send_message(callback_query.from_user.id, "Нажмите на кнопку Завершить чтобы отправить ответы", reply_markup=inline_kb_form)
        # Set state to end form
        await Form.form_end.set()
        return
    if data[2][i] == "Одиночный выбор":
        for k,j in enumerate(data[3][i].split(",")):
            text = str(j.strip())
            call_back = "active_"+ str(k)
            inline_kb_form.add(types.InlineKeyboardButton(text=text, callback_data=call_back))
    else:
        await Form.form_input.set()
        # inline_kb_form.add(types.InlineKeyboardButton(text=data[3][i], callback_data="active_"))
    if data[4][i] != "":
        await bot.send_photo(callback_query.from_user.id, data[4][i])
    await bot.send_message(callback_query.from_user.id, data[1][i], reply_markup=inline_kb_form)

async def process_callback_button3(message: types.Message, state: FSMContext):
    answ = message.text
    datas = await state.get_data()
    datas["answers"].append(answ)
    await state.update_data(answers=datas["answers"])
    i = await state.get_data()
    i = i["i"]
    print(i)
    await state.update_data(i=datas["i"]+1)
    inline_kb_form = types.InlineKeyboardMarkup()  
    record = await state.get_data()
    record = record["record"]
    with open(record, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    n = len(data[1])
    if i > n-1:
        inline_kb_form.add(types.InlineKeyboardButton(text="Завершить", callback_data="endForm_"))
        await bot.send_message(message.from_user.id, "Нажмите на кнопку Завершить чтобы отправить ответы", reply_markup=inline_kb_form)
        # Set state to end form
        await Form.form_end.set()
        return
    if data[2][i] == "Одиночный выбор":
        await Form.start.set()
        for k,j in enumerate(data[3][i].split(",")):
            text = str(j.strip())
            call_back = "active_"+ str(k)
            inline_kb_form.add(types.InlineKeyboardButton(text=text, callback_data=call_back))
    else:
        await Form.form_input.set()
    if data[4][i] != "":
        await bot.send_photo(message.from_user.id, data[4][i])
    await bot.send_message(message.from_user.id, data[1][i], reply_markup=inline_kb_form)

async def process_callback_button4(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # Write to state data from callback query
    # get data from state and insert to database
    datas = await state.get_data()
    answers = datas["answers"]
    # Get questions from csv file
    record = await state.get_data()
    record = record["record"]
    with open(record, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    qeustions = data[1]
    sql = '''INSERT INTO "''' + record.split(".")[0].split("/")[1].replace(" ", "_") + '''" '''
    sql += "( user_id,"
    for i in qeustions:
        if i == "Вопрос":
            continue
        sql += i.replace(" ", "_") + ", "
    sql = sql[:-2]
    sql += ") VALUES ( "
    user_id = callback_query.from_user.id
    sql += str(user_id).replace("'", "").replace("[", "").replace("]", "").replace("\"", "") + ", "
    for i in answers:
        if type(i) == list:
            # COnvert list to string
            i = ",".join(i)
        sql += "'" + i.replace(" ", "_").replace("'", "").replace("[", "").replace("]", "").replace("\"", "") + "', "
    sql = sql[:-2]
    sql += ");"
    print(sql)
    connection, cursor = await connect()
    cursor.execute(sql)
    connection.commit()
    # Get profile from database
    cursor.execute("SELECT promo FROM promos;")
    promos = []
    for row in cursor:
        promos.append(row[0])
    if promos == []:
        await bot.send_message(callback_query.from_user.id, "Ваши ответы успешно отправлены")
        return
    await bot.send_message(callback_query.from_user.id, "Ваши ответы успешно отправлены \nВаш проокд: " + str(random.choice(promos)))



def form_handler(dp):
    dp.register_callback_query_handler(process_callback_button1, lambda c: c.data.split("_")[0] == "form", state="Form:start")
    dp.register_callback_query_handler(process_callback_button2, lambda c: c.data.split("_")[0] == "active", state="Form:start")
    dp.register_message_handler(process_callback_button3, state="Form:form_input")
    dp.register_callback_query_handler(process_callback_button4, lambda c: c.data.split("_")[0] == "endForm", state="Form:form_end")
