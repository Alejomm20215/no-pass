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
from app.adapters.strategies.huggingface_attack import HuggingFaceAttack, HuggingFaceAIGenerator


class CrackPasswordUseCase:
    """Use case for cracking PDF password"""

    def __init__(
        self,
        pdf_handler: IPDFHandler,
        wordlist_provider: IWordlistProvider,
        hf_generator: Optional[HuggingFaceAIGenerator] = None
    ):
        self.pdf_handler = pdf_handler
        self.wordlist_provider = wordlist_provider
        self.hf_generator = hf_generator
    
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
        try:
            is_protected = self.pdf_handler.is_protected(pdf_path)
            if not is_protected:
                return CrackResult(
                    success=False,
                    error="PDF is not password protected"
                )
        except (FileNotFoundError, PermissionError) as e:
            # Re-raise file system errors
            return CrackResult(
                success=False,
                error=str(e)
            )
        except Exception as e:
            # If we can't determine protection status, log warning but continue
            # Some PDFs might have restrictions that aren't detected properly
            if progress_callback:
                progress_callback(0.0, f"Warning: Could not determine protection status: {e}")
            # Continue with attack - some PDFs might still be protected despite detection failure
        
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
        elif options.mode == AttackMode.AI_ATTACK:
            if not self.hf_generator:
                return CrackResult(
                    success=False,
                    error="AI generator not available"
                )
            strategy = HuggingFaceAttack(self.pdf_handler, self.hf_generator)
        else:
            return CrackResult(
                success=False,
                error=f"Unsupported attack mode: {options.mode}"
            )
        
        # Execute attack
        result = strategy.execute(pdf_path, progress_callback)
        return result

