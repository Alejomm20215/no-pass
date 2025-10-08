"""API schemas for password cracking"""

from typing import Optional
from pydantic import BaseModel, Field

from app.core.domain.entities import AttackMode, CharsetType, JobStatus


class CrackRequest(BaseModel):
    """Request to crack a PDF password"""
    mode: AttackMode = Field(AttackMode.DICTIONARY, description="Attack mode")
    charset: CharsetType = Field(CharsetType.NUMERIC, description="Character set for brute force")
    min_length: int = Field(1, ge=1, le=10, description="Minimum password length")
    max_length: int = Field(4, ge=1, le=10, description="Maximum password length")
    max_attempts: int = Field(10000, ge=1, description="Maximum attempts")
    custom_wordlist: Optional[list[str]] = Field(None, description="Custom wordlist")
    wordlist_file: Optional[str] = Field(None, description="Path to wordlist file (server-side)")
    john_binary: Optional[str] = Field(None, description="Path to John the Ripper binary")
    pdf2john_binary: Optional[str] = Field(None, description="Path to pdf2john.pl")
    pdfcrack_binary: Optional[str] = Field(None, description="Path to pdfcrack binary")
    timeout: int = Field(3600, ge=1, description="Timeout in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mode": "dictionary",
                "charset": "numeric",
                "min_length": 1,
                "max_length": 6,
                "max_attempts": 100000
            }
        }


class CrackResponse(BaseModel):
    """Response from crack attempt"""
    success: bool
    password: Optional[str] = None
    method: Optional[str] = None
    attempts: int = 0
    duration: float = 0.0
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "password": "123456",
                "method": "dictionary",
                "attempts": 234,
                "duration": 12.5
            }
        }


class UnlockRequest(BaseModel):
    """Request to unlock a PDF"""
    password: str = Field(..., description="The password to unlock PDF")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "123456"
            }
        }


class UnlockResponse(BaseModel):
    """Response from unlock attempt"""
    success: bool
    output_filename: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "output_filename": "document_unlocked.pdf"
            }
        }

