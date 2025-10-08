"""Dictionary attack strategy"""

from pathlib import Path
from typing import Optional, Callable
import time

from app.core.interfaces.attack_strategy import IAttackStrategy
from app.core.interfaces.pdf_handler import IPDFHandler
from app.core.domain.entities import CrackResult


class DictionaryAttack(IAttackStrategy):
    """Dictionary-based password attack"""
    
    def __init__(self, pdf_handler: IPDFHandler, wordlist: list[str]):
        self.pdf_handler = pdf_handler
        self.wordlist = wordlist
    
    def execute(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> CrackResult:
        """Execute dictionary attack"""
        start_time = time.time()
        total = len(self.wordlist)
        
        for idx, password in enumerate(self.wordlist, 1):
            # Update progress
            if progress_callback and idx % 10 == 0:
                progress = (idx / total) * 100
                progress_callback(progress, f"Trying password {idx}/{total}")
            
            # Try password
            if self.pdf_handler.try_password(pdf_path, password):
                duration = time.time() - start_time
                return CrackResult(
                    success=True,
                    password=password,
                    method="dictionary",
                    attempts=idx,
                    duration=duration
                )
        
        # No password found
        duration = time.time() - start_time
        return CrackResult(
            success=False,
            method="dictionary",
            attempts=total,
            duration=duration
        )
    
    def estimate_time(self) -> float:
        """Estimate time in seconds"""
        # Rough estimate: ~100 passwords per second
        return len(self.wordlist) / 100
    
    def estimate_attempts(self) -> int:
        """Estimate number of attempts"""
        return len(self.wordlist)

