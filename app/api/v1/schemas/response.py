"""Common API response schemas"""

from typing import Optional, Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Error response"""

    error: str
    detail: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "File not found",
                "detail": "The specified PDF file does not exist",
            }
        }


class SuccessResponse(BaseModel):
    """Success response"""

    success: bool = True
    message: str
    data: Optional[Any] = None

    class Config:
        json_schema_extra = {
            "example": {"success": True, "message": "Operation completed successfully"}
        }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = "healthy"
    version: str

    class Config:
        json_schema_extra = {"example": {"status": "healthy", "version": "1.0.0"}}
