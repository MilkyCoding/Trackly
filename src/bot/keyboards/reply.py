from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📊 Мои отслеживания")],
        [KeyboardButton(text="➕ Добавить товар")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_marketplace_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Ozon"), KeyboardButton(text="Wildberries")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
