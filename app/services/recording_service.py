from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from fastapi import HTTPException, status

from app.models.song import Recording
from app.models.user import User
from app.schemas.song import (
    RecordingCreate, 
    RecordingUpdate,
    RecordingResponse,
    RecordingsListResponse
)


class RecordingService:
    """Service for managing user recordings"""

    def create_recording(self, db: Session, recording_data: RecordingCreate, user_id: int) -> RecordingResponse:
        """Create a new recording for a user"""
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Convert notes to proper format for database
        notes_json = []
        for note in recording_data.notes:
            notes_json.append({
                "note": note.note,
                "octave": note.octave,
                "start_time": note.start_time,
                "end_time": note.end_time,
                "velocity": note.velocity
            })
        
        # Create recording
        db_recording = Recording(
            title=recording_data.title,
            description=recording_data.description,
            notes=notes_json,
            duration=recording_data.duration,
            tempo=recording_data.tempo,
            category=recording_data.category,
            user_id=user_id
        )
        
        db.add(db_recording)
        db.commit()
        db.refresh(db_recording)
        
        return RecordingResponse.from_orm(db_recording)

    def get_user_recordings(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        per_page: int = 20,
        category: Optional[str] = None
    ) -> RecordingsListResponse:
        """Get recordings for a user with pagination"""
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Build query
        query = db.query(Recording).filter(Recording.user_id == user_id)
        
        if category:
            query = query.filter(Recording.category == category)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        recordings = query.order_by(desc(Recording.created_at))\
                         .offset((page - 1) * per_page)\
                         .limit(per_page)\
                         .all()
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return RecordingsListResponse(
            recordings=[RecordingResponse.from_orm(r) for r in recordings],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def get_recording(self, db: Session, recording_id: int, user_id: int) -> RecordingResponse:
        """Get a specific recording by ID for a user"""
        
        recording = db.query(Recording).filter(
            and_(Recording.id == recording_id, Recording.user_id == user_id)
        ).first()
        
        if not recording:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grabación no encontrada"
            )
        
        return RecordingResponse.from_orm(recording)

    def update_recording(
        self, 
        db: Session, 
        recording_id: int, 
        user_id: int, 
        recording_data: RecordingUpdate
    ) -> RecordingResponse:
        """Update a recording"""
        
        recording = db.query(Recording).filter(
            and_(Recording.id == recording_id, Recording.user_id == user_id)
        ).first()
        
        if not recording:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grabación no encontrada"
            )
        
        # Update fields if provided
        if recording_data.title is not None:
            recording.title = recording_data.title
        if recording_data.description is not None:
            recording.description = recording_data.description
        if recording_data.tempo is not None:
            recording.tempo = recording_data.tempo
        if recording_data.category is not None:
            recording.category = recording_data.category
        
        db.commit()
        db.refresh(recording)
        
        return RecordingResponse.from_orm(recording)

    def delete_recording(self, db: Session, recording_id: int, user_id: int) -> bool:
        """Delete a recording"""
        
        recording = db.query(Recording).filter(
            and_(Recording.id == recording_id, Recording.user_id == user_id)
        ).first()
        
        if not recording:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grabación no encontrada"
            )
        
        db.delete(recording)
        db.commit()
        
        return True

    def get_recording_categories(self, db: Session, user_id: int) -> List[str]:
        """Get all unique categories for a user's recordings"""
        
        categories = db.query(Recording.category)\
                      .filter(Recording.user_id == user_id)\
                      .distinct()\
                      .all()
        
        return [category[0] for category in categories if category[0]]


# Create a singleton instance
recording_service = RecordingService()
