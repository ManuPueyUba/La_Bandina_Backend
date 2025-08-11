"""
Create database tables
"""
from app.core.database import Base, engine
from app.models.user import User
from app.models.song import Song, Recording, MidiFile
from app.models.composition import Composition
from app.models.key_mapping import KeyMapping

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Print created tables
    print(f"Created tables: {list(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    create_tables()
