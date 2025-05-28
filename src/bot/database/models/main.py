from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .base import Base
from .user import User
from .track import Track

def register_models() -> None:
    # Create all tables
    engine = create_engine("sqlite:///./trackly.db", connect_args={"check_same_thread": False})
    
    Base.metadata.create_all(bind=engine)
