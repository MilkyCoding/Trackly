from sqlalchemy.orm import Session
from src.bot.database.models.track import Track
import logging

def update_track_status(db: Session, track_id: int, is_active: bool) -> None:
    """Update track's active status."""
    logging.info(f"Updating track {track_id} status to {is_active}")
    track = db.query(Track).filter(Track.id == track_id).first()

    if track:
        logging.info(f"Found track: {track.id}, current status: {track.is_active}")

        track.is_active = is_active
        
        db.commit()
        db.refresh(track)
        
        logging.info(f"Updated track status to: {track.is_active}")
    else:
        logging.warning(f"Track {track_id} not found")

def update_track_price(db: Session, track_id: int, new_price: float) -> None:
    """Update track's current price."""
    track = db.query(Track).filter(Track.id == track_id).first()
    
    if track:
        track.current_price = new_price
        db.commit()
        db.refresh(track)
