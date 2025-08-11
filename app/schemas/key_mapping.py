from pydantic import BaseModel
from typing import Dict, Any, Optional

class KeyMappingBase(BaseModel):
    name: str
    mapping_data: Dict[str, Any]

class KeyMappingCreate(KeyMappingBase):
    pass

class KeyMappingUpdate(KeyMappingBase):
    name: Optional[str] = None
    mapping_data: Optional[Dict[str, Any]] = None

class KeyMappingResponse(KeyMappingBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
