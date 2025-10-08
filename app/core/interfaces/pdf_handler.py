"""Interface for PDF handling operations"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.core.domain.entities import PDFDocument, UnlockResult


class IPDFHandler(ABC):
    """Interface for PDF operations"""
    
    @abstractmethod
    def is_protected(self, pdf_path: Path) -> bool:
        """Check if PDF is password protected"""
        pass
    
    @abstractmethod
    def try_password(self, pdf_path: Path, password: str) -> bool:
        """Try opening PDF with given password"""
        pass
    
    @abstractmethod
    def unlock_pdf(
        self,
        pdf_path: Path,
        password: str,
        output_path: Optional[Path] = None
    ) -> UnlockResult:
        """Remove password protection from PDF"""
        pass
    
    @abstractmethod
    def get_pdf_info(self, pdf_path: Path) -> PDFDocument:
        """Get PDF metadata"""
        pass

