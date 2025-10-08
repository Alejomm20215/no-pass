"""Use case: Batch process multiple PDFs"""

from pathlib import Path
from typing import Optional, Callable, Dict

from app.core.domain.entities import (
    CrackJob,
    CrackResult,
    UnlockResult,
    AttackOptions,
    JobStatus,
)
from app.core.use_cases.crack_password import CrackPasswordUseCase
from app.core.use_cases.unlock_pdf import UnlockPDFUseCase
from app.core.interfaces.pdf_handler import IPDFHandler


class BatchProcessUseCase:
    """Use case for batch processing multiple PDFs"""
    
    def __init__(
        self,
        crack_use_case: CrackPasswordUseCase,
        unlock_use_case: UnlockPDFUseCase,
        pdf_handler: IPDFHandler
    ):
        self.crack_use_case = crack_use_case
        self.unlock_use_case = unlock_use_case
        self.pdf_handler = pdf_handler
    
    def execute(
        self,
        directory: Path,
        options: AttackOptions,
        progress_callback: Optional[Callable[[str, float, str], None]] = None,
        auto_unlock: bool = True,
        keep_originals: bool = True
    ) -> Dict[str, Dict]:
        """
        Process all PDFs in a directory
        
        Args:
            directory: Directory containing PDFs
            options: Attack options
            progress_callback: Optional callback (filename, progress%, message)
            auto_unlock: Automatically unlock if password found
            keep_originals: Keep original protected PDFs
            
        Returns:
            Dictionary with results for each file
        """
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory: {directory}")
        
        # Find all PDFs
        pdf_files = list(directory.glob("*.pdf"))
        results = {}
        
        for pdf_file in pdf_files:
            filename = pdf_file.name
            
            # Check if protected
            if not self.pdf_handler.is_protected(pdf_file):
                results[filename] = {
                    "status": "not_protected",
                    "message": "PDF is not password protected"
                }
                continue
            
            # Crack password
            def file_progress(progress: float, message: str):
                if progress_callback:
                    progress_callback(filename, progress, message)
            
            crack_result = self.crack_use_case.execute(
                pdf_file,
                options,
                file_progress
            )
            
            if not crack_result.success:
                results[filename] = {
                    "status": "failed",
                    "message": "Password not found",
                    "crack_result": crack_result
                }
                continue
            
            # Password found
            result_data = {
                "status": "success",
                "password": crack_result.password,
                "method": crack_result.method,
                "attempts": crack_result.attempts,
                "duration": crack_result.duration,
                "crack_result": crack_result
            }
            
            # Auto unlock if requested
            if auto_unlock:
                output_path = pdf_file.with_name(f"{pdf_file.stem}_unlocked.pdf")
                unlock_result = self.unlock_use_case.execute(
                    pdf_file,
                    crack_result.password,
                    output_path
                )
                
                result_data["unlocked"] = unlock_result.success
                result_data["unlock_result"] = unlock_result
                
                if unlock_result.success:
                    result_data["output_path"] = str(unlock_result.unlocked_path)
                    
                    # Delete original if requested
                    if not keep_originals:
                        try:
                            pdf_file.unlink()
                            result_data["original_deleted"] = True
                        except Exception as e:
                            result_data["original_deleted"] = False
                            result_data["delete_error"] = str(e)
            
            results[filename] = result_data
        
        return results

