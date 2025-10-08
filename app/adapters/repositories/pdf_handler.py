"""PDF handler implementation using pikepdf"""

from pathlib import Path
from typing import Optional
import sys
import os
import logging

logger = logging.getLogger(__name__)

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

    def _validate_pdf_path(self, pdf_path: Path) -> None:
        """Validate PDF file path and basic properties"""
        # Check if path exists and is a file
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not pdf_path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")

        # Check for symlinks to prevent symlink attacks
        if pdf_path.is_symlink():
            # Resolve symlink and check if target is within allowed directories
            resolved = pdf_path.resolve()
            # For security, we could add path traversal checks here
            if not str(resolved).startswith(str(pdf_path.parent)):
                raise ValueError(f"Symlink points outside parent directory: {pdf_path}")

        # Check file size (prevent memory exhaustion)
        file_size = pdf_path.stat().st_size
        max_size = 100 * 1024 * 1024  # 100MB limit
        if file_size > max_size:
            raise ValueError(f"PDF file too large ({file_size} bytes > {max_size} bytes): {pdf_path}")

        # Check file permissions
        if not os.access(pdf_path, os.R_OK):
            raise PermissionError(f"No read permission for file: {pdf_path}")

    def is_protected(self, pdf_path: Path) -> bool:
        """Check if PDF is password protected"""
        self._validate_pdf_path(pdf_path)

        try:
            with pikepdf.open(pdf_path):
                return False  # Opened without password - not protected
        except pikepdf.PasswordError:
            return True  # Requires password - protected
        except (FileNotFoundError, PermissionError) as e:
            # Re-raise file system errors
            raise
        except Exception as e:
            # For other exceptions (corrupted PDF, etc.), assume it might be protected
            # This is safer than assuming unprotected
            logger.warning(f"Could not determine protection status for {pdf_path.name}: {e}")
            logger.warning("Assuming protected to be safe - will attempt password cracking")
            return True
    
    def try_password(self, pdf_path: Path, password: str) -> bool:
        """Try opening PDF with given password"""
        self._validate_pdf_path(pdf_path)

        # Validate password input
        if not password or not isinstance(password, str):
            return False

        try:
            with pikepdf.open(pdf_path, password=password):
                return True
        except pikepdf.PasswordError:
            return False
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"File system error trying password on {pdf_path.name}: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error trying password on {pdf_path.name}: {e}")
            return False
    
    def unlock_pdf(
        self,
        pdf_path: Path,
        password: str,
        output_path: Optional[Path] = None
    ) -> UnlockResult:
        """Remove password protection from PDF"""
        self._validate_pdf_path(pdf_path)

        if output_path is None:
            output_path = pdf_path.with_name(f"{pdf_path.stem}_unlocked.pdf")

        # Validate output path
        if output_path.exists():
            # Check if we can write to the output location
            if not os.access(output_path.parent, os.W_OK):
                return UnlockResult(
                    success=False,
                    error=f"No write permission in output directory: {output_path.parent}"
                )

        # Validate password
        if not password or not isinstance(password, str):
            return UnlockResult(
                success=False,
                error="Invalid password provided"
            )

        try:
            # Open with password
            pdf = pikepdf.open(pdf_path, password=password)

            # Save without encryption
            pdf.save(output_path)
            pdf.close()

            return UnlockResult(
                success=True,
                unlocked_path=output_path
            )
        except pikepdf.PasswordError:
            return UnlockResult(
                success=False,
                error="Incorrect password"
            )
        except (FileNotFoundError, PermissionError) as e:
            return UnlockResult(
                success=False,
                error=f"File system error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error unlocking {pdf_path.name}: {e}")
            return UnlockResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    def get_pdf_info(self, pdf_path: Path) -> PDFDocument:
        """Get PDF metadata"""
        self._validate_pdf_path(pdf_path)

        try:
            size = pdf_path.stat().st_size
            is_protected = self.is_protected(pdf_path)

            return PDFDocument(
                filename=pdf_path.name,
                file_path=pdf_path,
                size=size,
                is_protected=is_protected
            )
        except Exception as e:
            logger.error(f"Error getting PDF info for {pdf_path.name}: {e}")
            # Return minimal info even if we can't determine protection status
            return PDFDocument(
                filename=pdf_path.name,
                file_path=pdf_path,
                size=pdf_path.stat().st_size,
                is_protected=True  # Assume protected if we can't determine
            )

