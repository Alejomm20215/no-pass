"""API schemas for PDF operations"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PDFInfo(BaseModel):
    """PDF information"""
    id: str
    filename: str
    size: int
    is_protected: bool
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "document.pdf",
                "size": 1024000,
                "is_protected": True,
                "created_at": "2025-01-08T10:00:00Z"
            }
        }


class UploadResponse(BaseModel):
    """Response from PDF upload"""
    id: str
    filename: str
    size: int
    is_protected: bool
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "document.pdf",
                "size": 1024000,
                "is_protected": True,
                "message": "File uploaded successfully"
            }
        }

