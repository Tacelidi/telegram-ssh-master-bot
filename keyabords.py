from aiogram.types import ReplyKeyboardMarkup
from aiogram import types


def start_kb() -> ReplyKeyboardMarkup:
    buttons = [
        [
            types.KeyboardButton(text="Мои сервера"),
            types.KeyboardButton(text="Добавить новый сервер")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Button menu",
        one_time_keyboard=True
    )
    return keyboard


def go_back_to_the_menu_kb() -> ReplyKeyboardMarkup:
    buttons = [
        [
            types.KeyboardButton(text="Вернутся в меню"),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Button menu",
        one_time_keyboard=True
    )
    return keyboard


def managing_servers_kb() -> ReplyKeyboardMarkup:
    buttons = [
        [
            types.KeyboardButton(text="Удалить сервер"),
            types.KeyboardButton(text="Изменить данные"),
            types.KeyboardButton(text="Подключение"),
            types.KeyboardButton(text="Получить данные"),
            types.KeyboardButton(text="Выход")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Button menu",
        one_time_keyboard=True
    )
    return keyboard


def server_commands() -> ReplyKeyboardMarkup:
    buttons = [
        [
            types.KeyboardButton(text="Отправить комманду"),
            types.KeyboardButton(text="Выключить"),
            types.KeyboardButton(text="Перезапустить")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Button menu",

    )
    return keyboard


def server_data() -> ReplyKeyboardMarkup:
    buttons = [
        [
            types.KeyboardButton(text="Имя сервера"),
            types.KeyboardButton(text="Имя пользователя"),
            types.KeyboardButton(text="Пароль"),
            types.KeyboardButton(text="Адрес")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Button menu"
    )
    return keyboard


def my_servers() -> ReplyKeyboardMarkup:
    buttons = [
        [
            types.KeyboardButton(text="Мои сервера"),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Button menu"
    )
    return keyboard
