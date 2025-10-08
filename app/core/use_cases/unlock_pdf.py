"""Use case: Unlock PDF by removing password"""

from pathlib import Path
from typing import Optional

from app.core.domain.entities import UnlockResult
from app.core.interfaces.pdf_handler import IPDFHandler


class UnlockPDFUseCase:
    """Use case for unlocking PDF"""

    def __init__(self, pdf_handler: IPDFHandler):
        self.pdf_handler = pdf_handler

    def execute(
        self, pdf_path: Path, password: str, output_path: Optional[Path] = None
    ) -> UnlockResult:
        """
        Unlock PDF by removing password

        Args:
            pdf_path: Path to the protected PDF
            password: The password
            output_path: Optional output path (default: <name>_unlocked.pdf)

        Returns:
            UnlockResult with the outcome
        """
        # Check if PDF exists
        if not pdf_path.exists():
            return UnlockResult(success=False, error=f"File not found: {pdf_path}")

        # Unlock the PDF
        result = self.pdf_handler.unlock_pdf(pdf_path, password, output_path)
        return result
