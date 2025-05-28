from sqlalchemy.orm import Session
from ..models.user import User
from ..models.track import Track

def get_user(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_tracks(db: Session, user_id: int) -> list[Track]:
    return db.query(Track).filter(Track.user_id == user_id, Track.is_active == True).all()

def get_active_tracks(db: Session) -> list[Track]:
    return db.query(Track).filter(Track.is_active == True).all()

def get_track(db: Session, track_id: int) -> Track:
    return db.query(Track).filter(Track.id == track_id).first()
