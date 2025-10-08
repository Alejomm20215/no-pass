"""Wordlist provider implementation"""

from pathlib import Path
from typing import Optional

from app.core.interfaces.wordlist_provider import IWordlistProvider
from app.core.domain.constants import DEFAULT_PASSWORDS


class FileWordlistProvider(IWordlistProvider):
    """Wordlist provider using file system"""
    
    def __init__(self, wordlist_dir: Optional[Path] = None):
        self.wordlist_dir = wordlist_dir or Path("config/wordlists")
        self.wordlist_dir.mkdir(parents=True, exist_ok=True)
    
    def get_default_wordlist(self) -> list[str]:
        """Get the default password wordlist"""
        return DEFAULT_PASSWORDS.copy()
    
    def load_wordlist(self, path: Path) -> list[str]:
        """Load custom wordlist from file"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith('#')
                ]
            return passwords
        except Exception as e:
            print(f"Error loading wordlist from {path}: {e}")
            return []
    
    def save_wordlist(self, wordlist: list[str], path: Path) -> bool:
        """Save wordlist to file"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for password in wordlist:
                    f.write(f"{password}\n")
            return True
        except Exception as e:
            print(f"Error saving wordlist to {path}: {e}")
            return False
    
    def get_wordlist_by_name(self, name: str) -> Optional[list[str]]:
        """Get wordlist by name"""
        if name == "default":
            return self.get_default_wordlist()
        
        # Try to load from file
        wordlist_path = self.wordlist_dir / f"{name}.txt"
        if wordlist_path.exists():
            return self.load_wordlist(wordlist_path)
        
        return None

