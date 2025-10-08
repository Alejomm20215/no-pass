"""Use case: Crack PDF password"""

from pathlib import Path
from typing import Optional, Callable

from app.core.domain.entities import (
    CrackJob,
    CrackResult,
    AttackOptions,
    AttackMode,
)
from app.core.domain.constants import CHARSET_MAP
from app.core.interfaces.pdf_handler import IPDFHandler
from app.core.interfaces.wordlist_provider import IWordlistProvider
from app.adapters.strategies.dictionary_attack import DictionaryAttack
from app.adapters.strategies.bruteforce_attack import BruteForceAttack
from app.adapters.strategies.hybrid_attack import HybridAttack
from app.adapters.strategies.john_attack import JohnTheRipperAttack
from app.adapters.strategies.pdfcrack_attack import PdfCrackAttack


class CrackPasswordUseCase:
    """Use case for cracking PDF password"""
    
    def __init__(
        self,
        pdf_handler: IPDFHandler,
        wordlist_provider: IWordlistProvider
    ):
        self.pdf_handler = pdf_handler
        self.wordlist_provider = wordlist_provider
    
    def execute(
        self,
        pdf_path: Path,
        options: AttackOptions,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> CrackResult:
        """
        Execute password cracking
        
        Args:
            pdf_path: Path to the PDF file
            options: Attack options
            progress_callback: Optional callback for progress updates
            
        Returns:
            CrackResult with the outcome
        """
        # Check if PDF exists
        if not pdf_path.exists():
            return CrackResult(
                success=False,
                error=f"File not found: {pdf_path}"
            )
        
        # Check if PDF is protected
        if not self.pdf_handler.is_protected(pdf_path):
            return CrackResult(
                success=False,
                error="PDF is not password protected"
            )
        
        # Get wordlist
        wordlist = options.wordlist
        if wordlist is None:
            wordlist = self.wordlist_provider.get_default_wordlist()

        # Ensure options has in-memory wordlist if available
        if options.wordlist is None and wordlist is not None:
            options.wordlist = wordlist
        
        # Get charset for brute force
        charset = CHARSET_MAP.get(options.charset.value, CHARSET_MAP["numeric"])
        
        # Choose attack strategy
        if options.mode == AttackMode.DICTIONARY:
            strategy = DictionaryAttack(self.pdf_handler, wordlist)
        elif options.mode == AttackMode.BRUTEFORCE:
            strategy = BruteForceAttack(
                self.pdf_handler,
                charset,
                options.min_length,
                options.max_length,
                options.max_attempts
            )
        elif options.mode == AttackMode.HYBRID:
            strategy = HybridAttack(
                self.pdf_handler,
                wordlist,
                charset,
                options.min_length,
                options.max_length,
                options.max_attempts
            )
        elif options.mode == AttackMode.JOHN_RIPPER:
            strategy = JohnTheRipperAttack(options)
        elif options.mode == AttackMode.PDFCRACK:
            strategy = PdfCrackAttack(options)
        else:
            return CrackResult(
                success=False,
                error=f"Unsupported attack mode: {options.mode}"
            )
        
        # Execute attack
        result = strategy.execute(pdf_path, progress_callback)
        return result

