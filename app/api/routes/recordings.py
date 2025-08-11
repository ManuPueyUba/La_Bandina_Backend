from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.song import (
    RecordingCreate,
    RecordingUpdate,
    RecordingResponse,
    RecordingsListResponse
)
from app.services.recording_service import recording_service

router = APIRouter()


@router.post("/", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
async def create_recording(
    recording_data: RecordingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recording for the current user"""
    return recording_service.create_recording(db, recording_data, current_user.id)


@router.get("/", response_model=RecordingsListResponse)
async def get_user_recordings(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recordings for the current user with pagination"""
    return recording_service.get_user_recordings(db, current_user.id, page, per_page, category)


@router.get("/categories", response_model=List[str])
async def get_recording_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all unique categories for the current user's recordings"""
    return recording_service.get_recording_categories(db, current_user.id)


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific recording by ID"""
    return recording_service.get_recording(db, recording_id, current_user.id)


@router.put("/{recording_id}", response_model=RecordingResponse)
async def update_recording(
    recording_id: int,
    recording_data: RecordingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a recording"""
    return recording_service.update_recording(db, recording_id, current_user.id, recording_data)


@router.delete("/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recording(
    recording_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a recording"""
    recording_service.delete_recording(db, recording_id, current_user.id)
    return None
