from sqlalchemy.orm import Session
from src.bot.database.models.track import Track

def delete_track(db: Session, track_id: int) -> None:
    """Delete a track by its ID."""
    track = db.query(Track).filter(Track.id == track_id).first()
    
    if track:
        db.delete(track)
        db.commit()
