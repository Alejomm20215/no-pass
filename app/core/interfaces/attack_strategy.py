"""Interface for password attack strategies"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Callable

from app.core.domain.entities import CrackResult


class IAttackStrategy(ABC):
    """Interface for password attack strategies"""
    
    @abstractmethod
    def execute(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> CrackResult:
        """
        Execute the attack strategy
        
        Args:
            pdf_path: Path to the PDF file
            progress_callback: Optional callback for progress updates (progress%, message)
            
        Returns:
            CrackResult with the outcome
        """
        pass
    
    @abstractmethod
    def estimate_time(self) -> float:
        """Estimate time in seconds for this attack"""
        pass
    
    @abstractmethod
    def estimate_attempts(self) -> int:
        """Estimate number of attempts"""
        pass

