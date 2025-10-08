# PDF Password Recovery Tools

A comprehensive suite of tools for working with password-protected PDF files using modern Python libraries and clean architecture principles.

## Overview

This project provides both **CLI tools** and a **REST API** for PDF password recovery and management, featuring multiple attack strategies and robust security practices.

### Core Features
- **Password Removal**: Unlock PDFs when you know the password
- **Password Cracking**: Multiple attack strategies (dictionary, brute force, AI-powered)
- **REST API**: FastAPI backend for mobile/web integration
- **Security**: Input validation, rate limiting, and comprehensive error handling
- **Clean Architecture**: Well-structured code with dependency injection and extensive testing
---

## Installation

### Prerequisites
- **Python 3.8+**
- **pip** package manager

### Dependencies
```bash
# Core dependencies
pip install pikepdf fastapi uvicorn pydantic python-multipart

# AI-powered features (optional, for local model inference)
pip install transformers torch

# Development dependencies
pip install pytest pytest-cov httpx
```

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd pdf-password-tools

# Install all dependencies
pip install -r requirements.txt

# Run tests to verify installation
python -m pytest tests/ -v
```

## Password Removal Tool

Remove password protection from PDF files when you know the password.

### Usage
```bash
# Basic usage (uses default password)
python scripts/cli_unlock.py protected.pdf -o unlocked.pdf

# With custom password
python scripts/cli_unlock.py protected.pdf -p "mypassword" -o unlocked.pdf

# Interactive password prompt
python scripts/cli_unlock.py protected.pdf -o unlocked.pdf --ask-password
```

---

## Password Cracking Tool

Advanced password recovery using multiple attack strategies.

### Quick Start Examples

```bash
# Dictionary attack (fastest for common passwords)
python scripts/cli_crack.py --file document.pdf --mode dictionary

# Brute force with numeric passwords (up to 6 digits)
python scripts/cli_crack.py --file document.pdf --mode bruteforce --max-length 6

# AI-powered contextual generation (no API keys needed)
python scripts/cli_crack.py --file invoice.pdf --mode ai_attack

# Batch processing entire directory
python scripts/cli_crack.py --directory ./pdfs --mode dictionary --save

# Custom wordlist with company-specific passwords
python scripts/cli_crack.py --file report.pdf --wordlist company_passwords.txt
```

### Attack Strategies

| Strategy | Description | Use Case | Speed |
|----------|-------------|----------|-------|
| **Dictionary** | Try common passwords | Most common scenario | Fast |
| **Brute Force** | Generate all combinations | Short passwords (≤6 chars) | Variable |
| **AI-Powered** | Context-aware generation | Intelligent guessing | Fast |
| **John the Ripper** | Advanced cracking | Professional scenarios | Slow |
| **PDFCrack** | PDF-specialized | PDF-specific patterns | Slow |
| **Hybrid** | Dictionary + Brute force | Comprehensive coverage | Variable |

---

## REST API Server

FastAPI backend for web/mobile integration.

### Starting the Server

```bash
# Development mode (with auto-reload)
python app/main.py

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Visit http://localhost:8000/docs for interactive API documentation
```

For full REST API details, start the server and open the interactive docs at `http://localhost:8000/docs`.

---

## Configuration

### Environment Variables

```bash
# Core settings
DEBUG=false
SECRET_KEY=your-secret-key-here

# File handling
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_DIR=data/uploads
OUTPUT_DIR=data/outputs

# AI model settings (optional)
AI_MODEL_NAME=distilgpt2
AI_MAX_TOKENS=50
AI_TEMPERATURE=0.8

# Performance tuning
MAX_ATTEMPTS_DEFAULT=10000
TIMEOUT_DEFAULT=3600
```

---

## Security & Ethics

### Important Guidelines

- **Legal Use Only**: Only process PDFs you own or have explicit permission for
- **Clean Up**: Delete unlocked files and temporary data after use
- **User Privileges**: Run with minimal required permissions
- **Verification**: Always verify PDF content after unlocking

### Security Features

- Input validation and sanitization
- File size and type restrictions
- Path traversal protection
- Rate limiting and abuse prevention
- Secure temporary file handling
- Comprehensive error handling

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **"Requires pikepdf"** | `pip install pikepdf` |
| **"File not found"** | Check file path and permissions |
| **"Not password protected"** | PDF has no opening password |
| **"Brute force too slow"** | Reduce `--max-length` or use `--charset numeric` |
| **"AI not available"** | Install: `pip install transformers torch` |
| **"External tool missing"** | Install John the Ripper or PDFCrack |
| **"Permission denied"** | Check file permissions and antivirus settings |

### Getting Help

1. Run `python cli_crack.py --help` for CLI options
2. Review test files in `tests/` for usage examples
3. Check `QUICKSTART.md` for common workflows

### Project Files

- **[LICENSE](LICENSE)**: MIT License terms
- **[SECURITY.md](SECURITY.md)**: Security policy and vulnerability reporting
- **[ETHICS.md](ETHICS.md)**: Legal use guidelines and ethical considerations
