from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class KeyMapping(Base):
    __tablename__ = "key_mappings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Name for the key mapping preset
    mapping_data = Column(JSON, nullable=False)  # JSON with the key mappings
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="key_mappings")
