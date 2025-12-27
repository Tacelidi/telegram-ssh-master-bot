import asyncio

from aiogram import Router, F, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.formatting import as_marked_section, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from SSH import SSHFullData
from keyabords import start_kb, go_back_to_the_menu_kb, managing_servers_kb, server_commands, server_data, my_servers,types
from DB import DataBase

db = DataBase()
router = Router()

from bot import bot

class UserState(StatesGroup):
    managing_servers = State()
    actioning_with_server = State()
    editing_server_pass = State()
    change_servername = State()
    change_username = State()
    change_password = State()
    change_address = State()
    connecting_server = State()
    send_command = State()
    waiting_name = State()
    waiting_address = State()
    waiting_username = State()
    waiting_password = State()


@router.message(F.text == "Вернутся в меню")
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Привет ,{html.bold(html.quote(message.from_user.first_name))}! Этот бот поможет управлять серверами через SSH🖥",
        reply_markup=start_kb())


@router.message(F.text == "Мои сервера")
async def servers(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    table_exists_flag = await db.table_exists(user_id)
    if not table_exists_flag:
        await message.answer(f"У вас нет таблицы с серверами.", reply_markup=go_back_to_the_menu_kb())
    else:
        servers_list = await db.get_servers(user_id)
        if len(servers_list) == 0:
            await message.answer(f"У вас уже есть таблица, но там нет серверов.",
                                 reply_markup=go_back_to_the_menu_kb())
        else:
            builder = ReplyKeyboardBuilder()
            for i in servers_list:
                builder.add(types.KeyboardButton(text=str(i)))
            builder.adjust(4)

            await message.answer(
                "Ваши сервера",
                reply_markup=builder.as_markup(resize_keyboard=True)
            )
            await state.set_state(UserState.managing_servers)


@router.message(UserState.managing_servers)
async def managing_servers(message: types.Message, state: FSMContext):
    await state.clear()
    server = message.text
    await message.answer("Что вы хотите сделать?", reply_markup=managing_servers_kb())
    await state.update_data(server=server)
    await state.set_state(UserState.actioning_with_server)


@router.message(UserState.actioning_with_server)
async def actioning_with_server(message: types.Message, state: FSMContext):
    server = await state.get_data()
    server = server['server']
    user_message = message.text
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    if user_message == "Подключение":
        await message.answer("Что вы хотите сделать?", reply_markup=server_commands())
        await state.set_state(UserState.connecting_server)
    elif user_message == "Выход":
        await message.answer(
            f"Привет ,{html.bold(html.quote(message.from_user.first_name))}! Этот бот поможет управлять серверами через SSH🖥",
            reply_markup=start_kb())
        await state.clear()
    elif user_message == "Удалить сервер":
        await db.delete_server(user_id, server)
        await message.answer("Сервер был удален")
        await message.answer(
            f"Привет ,{html.bold(html.quote(message.from_user.first_name))}! Этот бот поможет управлять серверами через SSH🖥",
            reply_markup=start_kb())
        await state.clear()
    elif user_message == "Получить данные":
        data = await db.get_connection_data(user_id, server)
        content = as_marked_section(
            Bold("Данные севера:"),
            f"Имя пользователя:{data[0]}",
            f"Пароль:{data[1]}",
            f"Адресс:{data[2]}"
        )
        await message.answer(**content.as_kwargs())
    elif user_message == "Изменить данные":
        await message.answer("Что вы хотите поменять?", reply_markup=server_data())
        await state.set_state(UserState.editing_server_pass)
    else:
        await state.set_state(UserState.actioning_with_server)


@router.message(UserState.connecting_server)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    server = await state.get_data()
    server = server['server']
    fl = True
    data = await db.get_connection_data(user_id, server)
    server_SSH = SSHFullData(data[0], data[1], data[2])
    loop = asyncio.get_event_loop()
    if user_message == "Отправить комманду":
        await state.set_state(UserState.send_command)
        await message.answer("Напишите комманду")
        fl = False
    if user_message == "Перезапустить":
        result = await loop.run_in_executor(None, server_SSH.restart)
        await message.answer(result, parse_mode=None)
        await state.clear()
        await message.answer("Вернутся в меню", reply_markup=start_kb())
    if user_message == "Выключить":
        result = await loop.run_in_executor(None, server_SSH.shutdown)
        await message.answer(result, parse_mode=None)
        await state.clear()
        await message.answer("Вернутся в меню", reply_markup=start_kb())
    if fl: await state.set_state(UserState.actioning_with_server)


@router.message(UserState.send_command)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    server = await state.get_data()
    server = server['server']
    data = await db.get_connection_data(user_id, server)
    server_SSH = SSHFullData(data[0], data[1], data[2])
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: server_SSH.send_command(user_message))
    await message.answer(result, parse_mode=None)
    await state.clear()
    await message.answer("Вернутся в меню", reply_markup=start_kb())


@router.message(UserState.editing_server_pass)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text
    if user_message == "Имя сервера":
        await message.answer("Введите новое имя сервера")
        await state.set_state(UserState.change_servername)
    elif user_message == "Имя пользователя":
        await message.answer("Введите новое имя пользователя")
        await state.set_state(UserState.change_username)
    elif user_message == "Пароль":
        await message.answer("Введите новый пароль")
        await state.set_state(UserState.change_password)
    elif user_message == "Адрес":
        await message.answer("Введите новый адрес")
        await state.set_state(UserState.change_address)


@router.message(UserState.change_servername)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text
    server = await state.get_data()
    server = server['server']
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    await db.change_servername(user_id, server, user_message)
    await message.answer("Успешно изменено", reply_markup=my_servers())
    await state.clear()


@router.message(UserState.change_username)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text
    server = await state.get_data()
    server = server['server']
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    await db.change_username(user_id, server, user_message)
    await message.answer("Успешно изменено", reply_markup=my_servers())
    await state.clear()


@router.message(UserState.change_password)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text
    server = await state.get_data()
    server = server['server']
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    await db.change_password(user_id, server, user_message)
    await message.answer("Успешно изменено", reply_markup=my_servers())
    await state.clear()


@router.message(UserState.change_address)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text
    server = await state.get_data()
    server = server['server']
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    await db.change_address(user_id, server, user_message)
    await message.answer("Успешно изменено", reply_markup=my_servers())
    await state.clear()


@router.message(F.text == "Добавить новый сервер")
async def new_server(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    table_exists = await db.table_exists(user_id)
    if not table_exists: await db.create_table(user_id)
    bot_msg = await message.answer("Назвоите ваш сервер")
    await state.update_data(bot_msg=bot_msg.message_id)
    await state.set_state(UserState.waiting_name)


@router.message(UserState.waiting_name)
async def process_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    server_name = message.text
    servers_list = await db.get_servers(user_id)
    if server_name in servers_list:
        await bot.edit_message_text("У вас уже есть такой сервер", chat_id=message.chat.id, message_id=data["bot_msg"])
        await message.answer("Вернутся в меню", reply_markup=start_kb())
        await state.clear()
    else:
        await state.update_data(server_name=server_name)
        await message.delete()
        await bot.edit_message_text("Введите адрес", chat_id=message.chat.id, message_id=data["bot_msg"])
        await state.set_state(UserState.waiting_address)


@router.message(UserState.waiting_address)
async def process_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(address=message.text)
    await message.delete()
    await bot.edit_message_text("Введите имя пользователя", chat_id=message.chat.id, message_id=data["bot_msg"])
    await state.set_state(UserState.waiting_username)


@router.message(UserState.waiting_username)
async def process_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(username=message.text)
    await message.delete()
    await bot.edit_message_text("Введите пароль", chat_id=message.chat.id, message_id=data["bot_msg"])
    await state.set_state(UserState.waiting_password)


@router.message(UserState.waiting_password)
async def process_message(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.delete()
    data = await state.get_data()
    user_id = str(message.from_user.first_name) + str(message.from_user.id)
    name = data["server_name"]
    address = data["address"]
    username = data["username"]
    password = data["password"]
    await db.add_server(user_id, name, username, password, address)
    await bot.delete_message(chat_id=message.chat.id, message_id=data["bot_msg"])
    await message.answer(f"Сервер \"{name}\" добавлен", reply_markup=start_kb())
    await state.clear()

