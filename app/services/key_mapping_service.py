from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.key_mapping import KeyMapping
from app.schemas.key_mapping import KeyMappingCreate, KeyMappingUpdate

class KeyMappingService:
    @staticmethod
    def create_key_mapping(db: Session, key_mapping: KeyMappingCreate, user_id: int) -> KeyMapping:
        """Crear una nueva configuración de teclas para un usuario"""
        db_key_mapping = KeyMapping(
            name=key_mapping.name,
            mapping_data=key_mapping.mapping_data,
            user_id=user_id
        )
        db.add(db_key_mapping)
        db.commit()
        db.refresh(db_key_mapping)
        return db_key_mapping
    
    @staticmethod
    def get_user_key_mappings(db: Session, user_id: int):
        """Obtener todas las configuraciones de teclas de un usuario"""
        return db.query(KeyMapping).filter(KeyMapping.user_id == user_id).all()
    
    @staticmethod
    def get_key_mapping_by_id(db: Session, key_mapping_id: int, user_id: int):
        """Obtener una configuración específica del usuario"""
        return db.query(KeyMapping).filter(
            and_(KeyMapping.id == key_mapping_id, KeyMapping.user_id == user_id)
        ).first()
    
    @staticmethod
    def update_key_mapping(db: Session, key_mapping_id: int, user_id: int, key_mapping_update: KeyMappingUpdate):
        """Actualizar una configuración de teclas"""
        db_key_mapping = db.query(KeyMapping).filter(
            and_(KeyMapping.id == key_mapping_id, KeyMapping.user_id == user_id)
        ).first()
        
        if not db_key_mapping:
            return None
            
        update_data = key_mapping_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_key_mapping, field, value)
        
        db.commit()
        db.refresh(db_key_mapping)
        return db_key_mapping
    
    @staticmethod
    def delete_key_mapping(db: Session, key_mapping_id: int, user_id: int):
        """Eliminar una configuración de teclas"""
        db_key_mapping = db.query(KeyMapping).filter(
            and_(KeyMapping.id == key_mapping_id, KeyMapping.user_id == user_id)
        ).first()
        
        if not db_key_mapping:
            return False
            
        db.delete(db_key_mapping)
        db.commit()
        return True
    
    @staticmethod
    def save_default_key_mapping(db: Session, user_id: int, mapping_data: dict) -> KeyMapping:
        """Guardar o actualizar la configuración de teclas por defecto del usuario"""
        # Buscar si ya existe una configuración por defecto
        existing = db.query(KeyMapping).filter(
            and_(KeyMapping.user_id == user_id, KeyMapping.name == "default")
        ).first()
        
        if existing:
            # Actualizar la existente
            existing.mapping_data = mapping_data
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Crear nueva
            db_key_mapping = KeyMapping(
                name="default",
                mapping_data=mapping_data,
                user_id=user_id
            )
            db.add(db_key_mapping)
            db.commit()
            db.refresh(db_key_mapping)
            return db_key_mapping
    
    @staticmethod
    def get_default_key_mapping(db: Session, user_id: int):
        """Obtener la configuración de teclas por defecto del usuario"""
        return db.query(KeyMapping).filter(
            and_(KeyMapping.user_id == user_id, KeyMapping.name == "default")
        ).first()
