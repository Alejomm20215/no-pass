"""Domain constants"""

import string

# Default password wordlist (most common passwords)
DEFAULT_PASSWORDS = [
    "123456",
    "password",
    "123456789",
    "12345678",
    "12345",
    "1234567",
    "1234567890",
    "qwerty",
    "abc123",
    "111111",
    "123123",
    "admin",
    "letmein",
    "welcome",
    "monkey",
    "password1",
    "1234",
    "dragon",
    "master",
    "123",
    "qwerty123",
    "654321",
    "Pass",
    "password123",
    "000000",
    "1q2w3e4r",
    "trustno1",
    "Password1",
    "admin123",
    "DEFAULT",
    "default",
    "test",
    "Test123",
    "password!",
    "Pass123",
    "Admin",
    "root",
    "toor",
    "changeme",
    "P@ssw0rd",
    "P@ssword",
    "passw0rd",
    "default_password",
    # Common international passwords
    "contraseña",
    "contrasena",
    "administrador",
    "usuario",
    # Common years
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025",
    # Typical combinations
    "abc123",
    "qwe123",
    "asd123",
    "pass123",
    "user123",
]

# Charset mappings for brute force
CHARSET_MAP = {
    "numeric": string.digits,
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "alphanumeric": string.ascii_lowercase + string.digits,
    "all": string.ascii_letters + string.digits,
}

# Default limits
DEFAULT_MAX_LENGTH = 4
DEFAULT_MIN_LENGTH = 1
DEFAULT_MAX_ATTEMPTS = 10000
DEFAULT_TIMEOUT = 3600  # 1 hour
