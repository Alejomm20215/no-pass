"""Interface for wordlist management"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List


class IWordlistProvider(ABC):
    """Interface for wordlist management"""

    @abstractmethod
    def get_default_wordlist(self) -> List[str]:
        """Get the default password wordlist"""
        pass

    @abstractmethod
    def load_wordlist(self, path: Path) -> List[str]:
        """Load custom wordlist from file"""
        pass

    @abstractmethod
    def save_wordlist(self, wordlist: List[str], path: Path) -> bool:
        """Save wordlist to file"""
        pass

    @abstractmethod
    def get_wordlist_by_name(self, name: str) -> Optional[List[str]]:
        """Get wordlist by name (e.g., 'default', 'numeric', 'common')"""
        pass
