"""
Create database tables
"""
from app.core.database import Base, engine
from app.models.user import User
from app.models.song import Song, Recording, MidiFile

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
