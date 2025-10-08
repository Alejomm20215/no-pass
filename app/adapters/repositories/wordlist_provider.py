"""Wordlist provider implementation"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

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
        # Validate file path
        if not path.exists():
            raise FileNotFoundError(f"Wordlist file not found: {path}")
        if not path.is_file():
            raise ValueError(f"Wordlist path is not a file: {path}")

        # Check file size to prevent memory issues
        max_size = 100 * 1024 * 1024  # 100MB limit for wordlists
        file_size = path.stat().st_size
        if file_size > max_size:
            raise ValueError(f"Wordlist file too large ({file_size} bytes > {max_size} bytes): {path}")

        try:
            # Try UTF-8 first, fallback to other encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            passwords = []

            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding, errors='strict') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Validate password format (basic sanity check)
                                if len(line) > 100:  # Reasonable password length limit
                                    logger.warning(f"Line {line_num} in {path.name} is very long (>{100} chars), skipping")
                                    continue
                                passwords.append(line)
                    break  # Success, exit encoding loop
                except UnicodeDecodeError:
                    continue  # Try next encoding
                except Exception as e:
                    logger.error(f"Error reading {path.name} with {encoding}: {e}")
                    continue

            if not passwords:
                logger.warning(f"No valid passwords found in {path.name}")
                return []

            # Remove duplicates while preserving order
            seen = set()
            unique_passwords = []
            for password in passwords:
                if password not in seen:
                    seen.add(password)
                    unique_passwords.append(password)

            logger.info(f"Loaded {len(unique_passwords)} unique passwords from {path.name}")
            return unique_passwords

        except Exception as e:
            logger.error(f"Error loading wordlist from {path}: {e}")
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

