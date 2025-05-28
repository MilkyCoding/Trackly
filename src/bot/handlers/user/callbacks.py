from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.bot.database.main import get_db
from src.bot.database.methods.get import get_track
from src.bot.database.methods.update import update_track_status
from src.bot.keyboards.inline import get_confirm_keyboard

router = Router()

@router.callback_query(F.data.startswith(("delete_track_", "pause_track_")))
async def process_track_callback(callback: CallbackQuery):
    action, track_id = callback.data.split("_")[1:]
    track_id = int(track_id)
    
    if action == "delete":
        await callback.message.edit_reply_markup(
            reply_markup=get_confirm_keyboard("delete", track_id)
        )
    elif action == "pause":
        await callback.message.edit_reply_markup(
            reply_markup=get_confirm_keyboard("pause", track_id)
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith(("confirm_", "cancel_")))
async def process_confirm_callback(callback: CallbackQuery):
    action, track_id = callback.data.split("_")[1:]
    track_id = int(track_id)
    
    db = next(get_db())
    track = get_track(db, track_id)
    
    if not track:
        await callback.answer("Товар не найден!")
        return
    
    if action == "delete":
        track.is_active = False
        db.commit()
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ Отслеживание удалено"
        )
    elif action == "pause":
        track.is_active = not track.is_active
        db.commit()
        status = "⏸ На паузе" if not track.is_active else "✅ Активно"
        await callback.message.edit_text(
            callback.message.text.split("\n📊 Статус:")[0] + f"\n📊 Статус: {status}"
        )
    
    await callback.answer()

def register_callback_handlers(dp: Router):
    dp.callback_query(F.data.startswith(("delete_track_", "pause_track_")))
    dp.callback_query(F.data.startswith(("confirm_", "cancel_"))) 