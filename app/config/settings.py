"""Application configuration"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App info
    APP_NAME: str = "PDF Password Recovery Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "data" / "outputs"
    WORDLIST_DIR: Path = BASE_DIR / "config" / "wordlists"
    
    # Limits
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    MAX_ATTEMPTS_DEFAULT: int = 10000
    TIMEOUT_DEFAULT: int = 3600  # 1 hour
    
    # Attack defaults
    DEFAULT_CHARSET: str = "numeric"
    DEFAULT_MIN_LENGTH: int = 1
    DEFAULT_MAX_LENGTH: int = 4
    
    # Security
    SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.WORDLIST_DIR.mkdir(parents=True, exist_ok=True)

    def validate(self):
        """Validate configuration settings"""
        errors = []

        # Check file size limit
        if self.MAX_FILE_SIZE <= 0:
            errors.append("MAX_FILE_SIZE must be positive")
        elif self.MAX_FILE_SIZE > 1024 * 1024 * 1024:  # 1GB
            errors.append("MAX_FILE_SIZE cannot exceed 1GB")

        # Check timeout values
        if self.TIMEOUT_DEFAULT <= 0:
            errors.append("TIMEOUT_DEFAULT must be positive")
        elif self.TIMEOUT_DEFAULT > 3600:  # 1 hour
            errors.append("TIMEOUT_DEFAULT cannot exceed 1 hour")

        # Check attack parameters
        if self.DEFAULT_MIN_LENGTH < 1:
            errors.append("DEFAULT_MIN_LENGTH must be at least 1")
        if self.DEFAULT_MAX_LENGTH > 10:
            errors.append("DEFAULT_MAX_LENGTH cannot exceed 10")
        if self.DEFAULT_MIN_LENGTH > self.DEFAULT_MAX_LENGTH:
            errors.append("DEFAULT_MIN_LENGTH cannot be greater than DEFAULT_MAX_LENGTH")

        # Check paths exist and are writable
        for path in [self.UPLOAD_DIR, self.OUTPUT_DIR, self.WORDLIST_DIR]:
            if not path.exists():
                errors.append(f"Directory does not exist: {path}")
            elif not path.is_dir():
                errors.append(f"Path is not a directory: {path}")

        if errors:
            raise ValueError(f"Configuration validation errors: {'; '.join(errors)}")

        return True


# Global settings instance
settings = Settings()

