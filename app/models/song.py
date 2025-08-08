from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Song(Base):
    __tablename__ = "songs"

    id = Column(String, primary_key=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    difficulty = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    category = Column(String(100), nullable=False)
    bpm = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)  # in milliseconds
    notes = Column(JSON, nullable=False)  # array of note objects
    key_signature = Column(String(20), default="C major")
    time_signature = Column(String(10), default="4/4")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(String, primary_key=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=False)  # in milliseconds
    notes = Column(JSON, nullable=False)  # array of recorded note objects
    bpm = Column(Integer, default=120)
    key_signature = Column(String(20), default="C major")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MidiFile(Base):
    __tablename__ = "midi_files"

    id = Column(String, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    processed = Column(Boolean, default=False)
    song_id = Column(String, nullable=True)  # FK to songs table
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
