from sqlalchemy.orm import Session
from ..models.user import User
from ..models.track import Track

def create_user(db: Session, user_id: int, username: str) -> User:
    """Create a new user."""
    user = User(user_id=user_id, username=username)
    
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def create_track(db: Session, user_id: int, product_url: str, target_price: float, marketplace: str, current_price: float = 0) -> Track:
    """Create a new track."""
    track = Track(
        user_id=user_id,
        product_url=product_url,
        current_price=current_price,
        target_price=target_price,
        marketplace=marketplace,
        is_active=True
    )
    db.add(track)
    db.commit()
    db.refresh(track)

    return track
