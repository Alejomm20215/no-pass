"""Hybrid attack strategy (dictionary + brute force)"""

from pathlib import Path
from typing import Optional, Callable

from app.core.interfaces.attack_strategy import IAttackStrategy
from app.core.interfaces.pdf_handler import IPDFHandler
from app.core.domain.entities import CrackResult
from app.adapters.strategies.dictionary_attack import DictionaryAttack
from app.adapters.strategies.bruteforce_attack import BruteForceAttack


class HybridAttack(IAttackStrategy):
    """Hybrid attack: dictionary first, then brute force"""
    
    def __init__(
        self,
        pdf_handler: IPDFHandler,
        wordlist: list[str],
        charset: str,
        min_length: int = 1,
        max_length: int = 4,
        max_attempts: int = 100000
    ):
        self.dictionary_attack = DictionaryAttack(pdf_handler, wordlist)
        self.bruteforce_attack = BruteForceAttack(
            pdf_handler, charset, min_length, max_length, max_attempts
        )
    
    def execute(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> CrackResult:
        """Execute hybrid attack"""
        
        # Phase 1: Dictionary attack (0-50% progress)
        def dict_progress(progress: float, message: str):
            if progress_callback:
                # Map to 0-50% range
                progress_callback(progress * 0.5, f"Dictionary: {message}")
        
        result = self.dictionary_attack.execute(pdf_path, dict_progress)
        if result.success:
            return result
        
        # Phase 2: Brute force attack (50-100% progress)
        def brute_progress(progress: float, message: str):
            if progress_callback:
                # Map to 50-100% range
                progress_callback(50 + progress * 0.5, f"Brute force: {message}")
        
        result = self.bruteforce_attack.execute(pdf_path, brute_progress)
        
        # Combine attempts from both phases
        total_attempts = (
            self.dictionary_attack.estimate_attempts() +
            result.attempts
        )
        result.attempts = total_attempts
        
        return result
    
    def estimate_time(self) -> float:
        """Estimate time in seconds"""
        return (
            self.dictionary_attack.estimate_time() +
            self.bruteforce_attack.estimate_time()
        )
    
    def estimate_attempts(self) -> int:
        """Estimate number of attempts"""
        return (
            self.dictionary_attack.estimate_attempts() +
            self.bruteforce_attack.estimate_attempts()
        )

