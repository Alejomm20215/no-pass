"""Dependency injection for FastAPI"""

from functools import lru_cache

from app.config.settings import Settings
from app.core.interfaces.pdf_handler import IPDFHandler
from app.core.interfaces.wordlist_provider import IWordlistProvider
from app.adapters.repositories.pdf_handler import PikePDFHandler
from app.adapters.repositories.wordlist_provider import FileWordlistProvider
from app.core.use_cases.crack_password import CrackPasswordUseCase
from app.core.use_cases.unlock_pdf import UnlockPDFUseCase
from app.core.use_cases.batch_process import BatchProcessUseCase
from typing import Optional, Any


@lru_cache()
def get_settings() -> Settings:
    """Get settings singleton"""
    settings = Settings()
    settings.validate()  # Validate configuration on first access
    return settings


@lru_cache()
def get_pdf_handler() -> IPDFHandler:
    """Get PDF handler singleton"""
    return PikePDFHandler()


@lru_cache()
def get_wordlist_provider() -> IWordlistProvider:
    """Get wordlist provider singleton"""
    settings = get_settings()
    return FileWordlistProvider(settings.WORDLIST_DIR)


@lru_cache()
def get_hf_generator() -> Optional[Any]:
    """AI generator not available in this build"""
    return None


def get_crack_password_use_case() -> CrackPasswordUseCase:
    """Get crack password use case"""
    return CrackPasswordUseCase(
        pdf_handler=get_pdf_handler(),
        wordlist_provider=get_wordlist_provider(),
        hf_generator=get_hf_generator()
    )


def get_unlock_pdf_use_case() -> UnlockPDFUseCase:
    """Get unlock PDF use case"""
    return UnlockPDFUseCase(
        pdf_handler=get_pdf_handler()
    )


def get_batch_process_use_case() -> BatchProcessUseCase:
    """Get batch process use case"""
    return BatchProcessUseCase(
        crack_use_case=get_crack_password_use_case(),
        unlock_use_case=get_unlock_pdf_use_case(),
        pdf_handler=get_pdf_handler()
    )

