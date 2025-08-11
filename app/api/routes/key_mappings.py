from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.key_mapping import KeyMappingCreate, KeyMappingResponse, KeyMappingUpdate
from app.services.key_mapping_service import KeyMappingService

router = APIRouter()

@router.post("/save-default", response_model=KeyMappingResponse, status_code=status.HTTP_200_OK)
def save_default_key_mapping(
    mapping_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Guardar o actualizar la configuración de teclas por defecto del usuario"""
    try:
        key_mapping = KeyMappingService.save_default_key_mapping(
            db=db,
            user_id=current_user.id,
            mapping_data=mapping_data
        )
        return key_mapping
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving key mapping: {str(e)}"
        )

@router.get("/default", response_model=KeyMappingResponse)
def get_default_key_mapping(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener la configuración de teclas por defecto del usuario"""
    key_mapping = KeyMappingService.get_default_key_mapping(
        db=db,
        user_id=current_user.id
    )
    
    if not key_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Default key mapping not found"
        )
    
    return key_mapping

@router.get("/", response_model=List[KeyMappingResponse])
def get_user_key_mappings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todas las configuraciones de teclas del usuario"""
    return KeyMappingService.get_user_key_mappings(db=db, user_id=current_user.id)

@router.post("/", response_model=KeyMappingResponse, status_code=status.HTTP_201_CREATED)
def create_key_mapping(
    key_mapping: KeyMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear una nueva configuración de teclas personalizada"""
    return KeyMappingService.create_key_mapping(
        db=db,
        key_mapping=key_mapping,
        user_id=current_user.id
    )

@router.put("/{key_mapping_id}", response_model=KeyMappingResponse)
def update_key_mapping(
    key_mapping_id: int,
    key_mapping_update: KeyMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar una configuración de teclas"""
    key_mapping = KeyMappingService.update_key_mapping(
        db=db,
        key_mapping_id=key_mapping_id,
        user_id=current_user.id,
        key_mapping_update=key_mapping_update
    )
    
    if not key_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key mapping not found"
        )
    
    return key_mapping

@router.delete("/{key_mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_key_mapping(
    key_mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar una configuración de teclas"""
    success = KeyMappingService.delete_key_mapping(
        db=db,
        key_mapping_id=key_mapping_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key mapping not found"
        )
