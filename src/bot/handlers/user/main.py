from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

from src.bot.database.main import get_db
from src.bot.database.models.track import Track
from src.bot.database.methods.create import create_user, create_track
from src.bot.database.methods.get import get_user, get_user_tracks
from src.bot.database.methods.update import update_track_status, update_track_price
from src.bot.database.methods.delete import delete_track
from src.bot.keyboards.reply import get_main_keyboard, get_marketplace_keyboard
from src.bot.keyboards.inline import get_track_keyboard, get_confirm_keyboard
from src.page_objects.price import OzonPrice, WildberriesPrice

router = Router()

class TrackStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_price = State()
    waiting_for_marketplace = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    db = next(get_db())
    user = get_user(db, message.from_user.id)
    if not user:
        create_user(db, message.from_user.id, message.from_user.username)
    
    await message.answer(
        "👋 Привет! Я бот для отслеживания цен на товары в Ozon и Wildberries.\n"
        "Используйте кнопки меню для управления отслеживаниями.",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "📊 Мои отслеживания")
async def show_tracks(message: Message):
    db = next(get_db())
    tracks = get_user_tracks(db, message.from_user.id)
    
    if not tracks:
        await message.answer("У вас пока нет отслеживаемых товаров.")
        return
    
    for track in tracks:
        status = "✅ Активно" if track.is_active else "⏸ На паузе"
        await message.answer(
            f"🛍 Товар: {track.product_url}\n"
            f"💰 Текущая цена: {track.current_price}₽\n"
            f"🎯 Целевая цена: {track.target_price}₽\n"
            f"🏪 Магазин: {track.marketplace}\n"
            f"📊 Статус: {status}",
            reply_markup=get_track_keyboard(track.id, db)
        )

@router.message(F.text == "➕ Добавить товар")
async def add_track_start(message: Message, state: FSMContext):
    await state.set_state(TrackStates.waiting_for_marketplace)
    await message.answer(
        "Выберите маркетплейс:",
        reply_markup=get_marketplace_keyboard()
    )

@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state:
        await state.clear()

    await message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message):
    help_text = (
        "🤖 <b>Trackly - бот для отслеживания цен</b>\n\n"
        "📝 <b>Основные команды:</b>\n"
        "• /start - Запустить бота\n"
        "• 📊 Мои отслеживания - Показать список отслеживаемых товаров\n"
        "• ➕ Добавить товар - Добавить новый товар для отслеживания\n"
        "• ❌ Удалить товар - Удалить товар из отслеживания\n\n"
        "📌 <b>Как использовать:</b>\n"
        "1. Нажмите '➕ Добавить товар'\n"
        "2. Выберите маркетплейс (Ozon или Wildberries)\n"
        "3. Отправьте ссылку на товар\n"
        "4. Укажите целевую цену\n\n"
        "🔔 <b>Уведомления:</b>\n"
        "• Бот будет проверять цены каждый час\n"
        "• Вы получите уведомление, когда цена упадет ниже целевой\n"
        "• Можно приостановить отслеживание, нажав '⏸ Пауза'"
    )

    await message.answer(help_text, reply_markup=get_main_keyboard())

@router.message(TrackStates.waiting_for_marketplace)
async def process_marketplace(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await back_to_main(message, state)
        return
        
    if message.text not in ["Ozon", "Wildberries"]:
        await message.answer("Пожалуйста, выберите маркетплейс из предложенных вариантов.")
        return
    
    await state.update_data(marketplace=message.text.lower())
    await state.set_state(TrackStates.waiting_for_url)

    await message.answer(
        "Отправьте ссылку на товар:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(TrackStates.waiting_for_url)
async def process_url(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.set_state(TrackStates.waiting_for_marketplace)
        await message.answer(
            "Выберите маркетплейс:",
            reply_markup=get_marketplace_keyboard()
        )
        return
        
    url = message.text

    if not (url.startswith("https://www.ozon.ru/") or url.startswith("https://www.wildberries.ru/")):
        await message.answer("Пожалуйста, отправьте корректную ссылку на товар.")
        return
    
    await state.update_data(product_url=url)
    await state.set_state(TrackStates.waiting_for_price)

    await message.answer(
        "Введите целевую цену (только число):",
        reply_markup=get_main_keyboard()
    )

async def check_price_immediately(url: str, marketplace: str, message: Message) -> tuple[int, str]:
    """Check price immediately after adding a new track."""
    try:
        # Отправляем сообщение о начале проверки
        status_message = await message.answer("🔄 Получаю информацию о товаре...")
        
        # Настраиваем Chrome
        options = uc.ChromeOptions()
        
        # Создаем драйвер с указанием версии
        await message.answer("🌐 Открываю страницу товара...")
        driver = uc.Chrome(
            options=options,
            version_main=136  # Указываем версию Chrome
        )
        
        # Получаем цену
        await message.answer("🔍 Ищу информацию о цене...")
        driver.get(url)
        
        if marketplace == "ozon":
            price_checker = OzonPrice(driver)
        else:
            price_checker = WildberriesPrice(driver)
        
        price = price_checker.get_price()
        driver.quit()
        
        if price == -1:
            return -1, "❌ Не удалось получить цену товара. Проверьте правильность ссылки."
        
        return price, "✅ Цена успешно получена"
    except Exception as e:
        logging.error(f"Error checking price: {str(e)}")
        return -1, f"❌ Ошибка при проверке цены: {str(e)}"

@router.message(TrackStates.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.set_state(TrackStates.waiting_for_url)
        await message.answer(
            "Отправьте ссылку на товар:",
            reply_markup=ReplyKeyboardRemove()
        )
        return
        
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return
    
    data = await state.get_data()
    db = next(get_db())
    
    # Проверяем цену перед добавлением
    current_price, status_message = await check_price_immediately(data["product_url"], data["marketplace"], message)
    
    if current_price == -1:
        await message.answer(
            f"{status_message}\nПопробуйте добавить товар позже или проверьте ссылку.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return
    
    # Создаем отслеживание с полученной ценой
    track = create_track(
        db,
        message.from_user.id,
        data["product_url"],
        price,
        data["marketplace"],
        current_price
    )
    
    await state.clear()
    await message.answer(
        f"{status_message}\n"
        f"💰 Текущая цена: {current_price}₽\n"
        f"🎯 Целевая цена: {price}₽\n\n"
        f"✅ Товар успешно добавлен для отслеживания!",
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data.startswith("delete_track_"))
async def delete_track_handler(callback: CallbackQuery):
    logging.info(f"Delete track handler called with data: {callback.data}")

    track_id = int(callback.data.split("_")[-1])

    await callback.message.edit_reply_markup(
        reply_markup=get_confirm_keyboard("delete", track_id)
    )

@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_handler(callback: CallbackQuery):
    logging.info(f"Confirm delete handler called with data: {callback.data}")

    try:
        track_id = int(callback.data.split("_")[-1])
        db = next(get_db())
        
        # Получаем информацию о треке перед удалением
        track = db.query(Track).filter(Track.id == track_id).first()

        if not track:
            await callback.answer("❌ Товар не найден")
            return
            
        # Удаляем трек
        delete_track(db, track_id)
        
        # Обновляем сообщение
        await callback.message.edit_text(
            f"❌ Товар удален из отслеживания:\n"
            f"🛍 {track.product_url}\n"
            f"🏪 {track.marketplace}"
        )
        await callback.answer("✅ Товар успешно удален")
    except Exception as e:
        logging.error(f"Error deleting track: {str(e)}")
        await callback.answer("❌ Ошибка при удалении товара")

@router.callback_query(F.data.startswith("cancel_delete_"))
async def cancel_delete_handler(callback: CallbackQuery):
    logging.info(f"Cancel delete handler called with data: {callback.data}")

    try:
        track_id = int(callback.data.split("_")[-1])
        db = next(get_db())

        await callback.message.edit_reply_markup(
            reply_markup=get_track_keyboard(track_id, db)
        )

        await callback.answer("❌ Удаление отменено")
    except Exception as e:
        logging.error(f"Error canceling delete: {str(e)}")
        await callback.answer("❌ Ошибка при отмене удаления")

@router.callback_query(F.data.startswith("pause_track_"))
async def pause_track_handler(callback: CallbackQuery):
    logging.info(f"Pause track handler called with data: {callback.data}")

    track_id = int(callback.data.split("_")[-1])

    await callback.message.edit_reply_markup(
        reply_markup=get_confirm_keyboard("pause", track_id)
    )

@router.callback_query(F.data.startswith("confirm_pause_"))
async def confirm_pause_handler(callback: CallbackQuery):
    logging.info(f"Confirm pause handler called with data: {callback.data}")
    track_id = int(callback.data.split("_")[-1])
    db = next(get_db())
    
    # Обновляем статус
    update_track_status(db, track_id, False)
    
    # Получаем обновленные данные
    track = db.query(Track).filter(Track.id == track_id).first()

    if track:
        logging.info(f"Track status after update: {track.is_active}")
        status = "⏸ На паузе" if not track.is_active else "✅ Активно"
        await callback.message.edit_text(
            f"🛍 Товар: {track.product_url}\n"
            f"💰 Текущая цена: {track.current_price}₽\n"
            f"🎯 Целевая цена: {track.target_price}₽\n"
            f"🏪 Магазин: {track.marketplace}\n"
            f"📊 Статус: {status}",
            reply_markup=get_track_keyboard(track_id, db)
        )

@router.callback_query(F.data.startswith("cancel_pause_"))
async def cancel_pause_handler(callback: CallbackQuery):
    logging.info(f"Cancel pause handler called with data: {callback.data}")
    track_id = int(callback.data.split("_")[-1])

    await callback.message.edit_reply_markup(
        reply_markup=get_track_keyboard(track_id)
    )

@router.callback_query(F.data.startswith("resume_track_"))
async def resume_track_handler(callback: CallbackQuery):
    logging.info(f"Resume track handler called with data: {callback.data}")
    track_id = int(callback.data.split("_")[-1])

    await callback.message.edit_reply_markup(
        reply_markup=get_confirm_keyboard("resume", track_id)
    )

@router.callback_query(F.data.startswith("confirm_resume_"))
async def confirm_resume_handler(callback: CallbackQuery):
    logging.info(f"Confirm resume handler called with data: {callback.data}")
    track_id = int(callback.data.split("_")[-1])
    db = next(get_db())
    
    # Обновляем статус
    update_track_status(db, track_id, True)
    
    # Получаем обновленные данные
    track = db.query(Track).filter(Track.id == track_id).first()

    if track:
        logging.info(f"Track status after update: {track.is_active}")
        status = "⏸ На паузе" if not track.is_active else "✅ Активно"
        await callback.message.edit_text(
            f"🛍 Товар: {track.product_url}\n"
            f"💰 Текущая цена: {track.current_price}₽\n"
            f"🎯 Целевая цена: {track.target_price}₽\n"
            f"🏪 Магазин: {track.marketplace}\n"
            f"📊 Статус: {status}",
            reply_markup=get_track_keyboard(track_id, db)
        )

@router.callback_query(F.data.startswith("cancel_resume_"))
async def cancel_resume_handler(callback: CallbackQuery):
    logging.info(f"Cancel resume handler called with data: {callback.data}")
    track_id = int(callback.data.split("_")[-1])
    db = next(get_db())
    
    await callback.message.edit_reply_markup(
        reply_markup=get_track_keyboard(track_id, db)
    )

def register_user_handlers(dp: Router):
    dp.register_message_handler(cmd_start, Command("start"))
    dp.register_message_handler(show_tracks, F.text == "📊 Мои отслеживания")
    dp.register_message_handler(add_track_start, F.text == "➕ Добавить товар")
    dp.register_message_handler(back_to_main, F.text == "🔙 Назад")
    dp.register_message_handler(show_help, F.text == "ℹ️ Помощь")
    
    dp.register_message_handler(process_marketplace, TrackStates.waiting_for_marketplace)
    dp.register_message_handler(process_url, TrackStates.waiting_for_url)
    dp.register_message_handler(process_price, TrackStates.waiting_for_price)
    
    dp.register_callback_query_handler(delete_track_handler, F.data.startswith("delete_track_"))
    dp.register_callback_query_handler(confirm_delete_handler, F.data.startswith("confirm_delete_"))
    dp.register_callback_query_handler(cancel_delete_handler, F.data.startswith("cancel_delete_"))
    dp.register_callback_query_handler(pause_track_handler, F.data.startswith("pause_track_"))
    dp.register_callback_query_handler(confirm_pause_handler, F.data.startswith("confirm_pause_"))
    dp.register_callback_query_handler(cancel_pause_handler, F.data.startswith("cancel_pause_"))
    dp.register_callback_query_handler(resume_track_handler, F.data.startswith("resume_track_"))
    dp.register_callback_query_handler(confirm_resume_handler, F.data.startswith("confirm_resume_"))
    dp.register_callback_query_handler(cancel_resume_handler, F.data.startswith("cancel_resume_"))

