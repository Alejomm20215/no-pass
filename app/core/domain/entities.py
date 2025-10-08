"""Domain entities - Core business objects"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List
from uuid import uuid4


class JobStatus(str, Enum):
    """Job processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AttackMode(str, Enum):
    """Password attack methods"""
    DICTIONARY = "dictionary"
    BRUTEFORCE = "bruteforce"
    HYBRID = "both"  # Try dictionary first, then bruteforce
    JOHN_RIPPER = "john"
    PDFCRACK = "pdfcrack"
    AI_ATTACK = "ai_attack"  # AI-powered contextual password generation


class CharsetType(str, Enum):
    """Character sets for brute force"""
    NUMERIC = "numeric"
    LOWERCASE = "lowercase"
    UPPERCASE = "uppercase"
    ALPHANUMERIC = "alphanumeric"
    ALL = "all"


@dataclass
class PDFDocument:
    """Represents a PDF document"""
    id: str = field(default_factory=lambda: str(uuid4()))
    filename: str = ""
    file_path: Optional[Path] = None
    size: int = 0
    is_protected: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.file_path and isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)


@dataclass
class AttackOptions:
    """Options for password attack"""
    mode: AttackMode = AttackMode.DICTIONARY
    charset: CharsetType = CharsetType.NUMERIC
    min_length: int = 1
    max_length: int = 4
    max_attempts: int = 10000
    wordlist: Optional[List[str]] = None
    wordlist_file: Optional[Path] = None
    john_binary: str = "john"
    pdf2john_binary: str = "pdf2john.pl"
    pdfcrack_binary: str = "pdfcrack"
    timeout: int = 3600  # seconds
    verbose: bool = False

    def __post_init__(self):
        if self.wordlist_file and isinstance(self.wordlist_file, str):
            self.wordlist_file = Path(self.wordlist_file)


@dataclass
class CrackResult:
    """Result of password cracking attempt"""
    success: bool
    password: Optional[str] = None
    method: Optional[str] = None  # "dictionary" or "bruteforce"
    attempts: int = 0
    duration: float = 0.0  # seconds
    error: Optional[str] = None


@dataclass
class CrackJob:
    """Represents a password cracking job"""
    id: str = field(default_factory=lambda: str(uuid4()))
    pdf_id: str = ""
    pdf_path: Optional[Path] = None
    status: JobStatus = JobStatus.QUEUED
    progress: float = 0.0  # 0-100
    options: Optional[AttackOptions] = None
    result: Optional[CrackResult] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.pdf_path and isinstance(self.pdf_path, str):
            self.pdf_path = Path(self.pdf_path)
        if self.options is None:
            self.options = AttackOptions()
    
    def start(self):
        """Mark job as started"""
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.now()
    
    def complete(self, result: CrackResult):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
        self.result = result
        self.progress = 100.0
        self.completed_at = datetime.now()
    
    def fail(self, error: str):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
    
    def cancel(self):
        """Cancel the job"""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def update_progress(self, progress: float):
        """Update job progress"""
        self.progress = min(100.0, max(0.0, progress))


@dataclass
class UnlockResult:
    """Result of PDF unlocking"""
    success: bool
    unlocked_path: Optional[Path] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.unlocked_path and isinstance(self.unlocked_path, str):
            self.unlocked_path = Path(self.unlocked_path)

