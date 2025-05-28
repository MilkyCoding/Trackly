from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.database.models.track import Track
from sqlalchemy.orm import Session

def get_track_keyboard(track_id: int, db: Session = None) -> InlineKeyboardMarkup:
    keyboard = []
    
    if db:
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if track and not track.is_active:
            # Если товар на паузе, показываем кнопку возобновления
            keyboard.append([
                InlineKeyboardButton(text="▶️ Возобновить", callback_data=f"resume_track_{track_id}"),
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_track_{track_id}")
            ])
            return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    # Стандартные кнопки для активного товара или если база данных не передана
    keyboard.append([
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_track_{track_id}"),
        InlineKeyboardButton(text="⏸ Пауза", callback_data=f"pause_track_{track_id}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirm_keyboard(action: str, track_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{track_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}_{track_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
