from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Track(Base):
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    product_url = Column(String)
    current_price = Column(Float)
    target_price = Column(Float)
    marketplace = Column(String)  # 'ozon' or 'wildberries'
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", backref="tracks")
    
    def __repr__(self):
        return f"<Track(product_url={self.product_url}, current_price={self.current_price})>" 