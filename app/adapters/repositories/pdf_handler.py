"""PDF handler implementation using pikepdf"""

from pathlib import Path
from typing import Optional
import sys

try:
    import pikepdf
except ImportError:
    print("Error: This module requires 'pikepdf'.", file=sys.stderr)
    print("Install it with: pip install pikepdf", file=sys.stderr)
    raise

from app.core.interfaces.pdf_handler import IPDFHandler
from app.core.domain.entities import PDFDocument, UnlockResult


class PikePDFHandler(IPDFHandler):
    """PDF handler using pikepdf library"""

    def is_protected(self, pdf_path: Path) -> bool:
        """Check if PDF is password protected"""
        try:
            with pikepdf.open(pdf_path):
                return False  # Opened without password
        except pikepdf.PasswordError:
            return True  # Requires password
        except Exception as e:
            print(f"Warning: Error checking {pdf_path.name}: {e}")
            return False

    def try_password(self, pdf_path: Path, password: str) -> bool:
        """Try opening PDF with given password"""
        try:
            with pikepdf.open(pdf_path, password=password):
                return True
        except pikepdf.PasswordError:
            return False
        except Exception:
            return False

    def unlock_pdf(
        self, pdf_path: Path, password: str, output_path: Optional[Path] = None
    ) -> UnlockResult:
        """Remove password protection from PDF"""
        if output_path is None:
            output_path = pdf_path.with_name(f"{pdf_path.stem}_unlocked.pdf")

        try:
            # Open with password
            pdf = pikepdf.open(pdf_path, password=password)

            # Save without encryption
            pdf.save(output_path)
            pdf.close()

            return UnlockResult(success=True, unlocked_path=output_path)
        except pikepdf.PasswordError:
            return UnlockResult(success=False, error="Incorrect password")
        except Exception as e:
            return UnlockResult(success=False, error=str(e))

    def get_pdf_info(self, pdf_path: Path) -> PDFDocument:
        """Get PDF metadata"""
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        size = pdf_path.stat().st_size
        is_protected = self.is_protected(pdf_path)

        return PDFDocument(
            filename=pdf_path.name,
            file_path=pdf_path,
            size=size,
            is_protected=is_protected,
        )
