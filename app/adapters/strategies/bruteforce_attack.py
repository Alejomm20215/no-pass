"""Brute force attack strategy"""

from pathlib import Path
from typing import Optional, Callable, Iterator
import time
import itertools

from app.core.interfaces.attack_strategy import IAttackStrategy
from app.core.interfaces.pdf_handler import IPDFHandler
from app.core.domain.entities import CrackResult


class BruteForceAttack(IAttackStrategy):
    """Brute force password attack"""

    def __init__(
        self,
        pdf_handler: IPDFHandler,
        charset: str,
        min_length: int = 1,
        max_length: int = 4,
        max_attempts: int = 10000,
    ):
        self.pdf_handler = pdf_handler
        self.charset = charset
        self.min_length = min_length
        self.max_length = max_length
        self.max_attempts = max_attempts

    def _generate_passwords(self) -> Iterator[str]:
        """Generate all possible password combinations"""
        for length in range(self.min_length, self.max_length + 1):
            for combination in itertools.product(self.charset, repeat=length):
                yield "".join(combination)

    def execute(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> CrackResult:
        """Execute brute force attack"""
        start_time = time.time()
        attempts = 0
        generator = self._generate_passwords()

        for password in generator:
            attempts += 1

            # Update progress
            if progress_callback and attempts % 100 == 0:
                progress = min(100, (attempts / self.max_attempts) * 100)
                progress_callback(progress, f"Attempt {attempts} (last: {password})")

            # Try password
            if self.pdf_handler.try_password(pdf_path, password):
                duration = time.time() - start_time
                return CrackResult(
                    success=True,
                    password=password,
                    method="bruteforce",
                    attempts=attempts,
                    duration=duration,
                )

            # Check max attempts limit
            if attempts >= self.max_attempts:
                break

        # No password found
        duration = time.time() - start_time
        return CrackResult(
            success=False,
            method="bruteforce",
            attempts=attempts,
            duration=duration,
            error=f"Reached max attempts ({self.max_attempts})",
        )

    def estimate_time(self) -> float:
        """Estimate time in seconds"""
        # Rough estimate: ~100 passwords per second
        return min(self.max_attempts, self.estimate_attempts()) / 100

    def estimate_attempts(self) -> int:
        """Estimate total number of attempts"""
        total = 0
        charset_len = len(self.charset)
        for length in range(self.min_length, self.max_length + 1):
            total += charset_len**length
        return total
