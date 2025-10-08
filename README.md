# PDF Password Recovery Tools

A comprehensive suite of tools for working with password-protected PDF files using modern Python libraries and clean architecture principles.

## Overview

This project provides both **CLI tools** and a **REST API** for PDF password recovery and management, featuring multiple attack strategies and robust security practices.

### Core Features
- **Password Removal**: Unlock PDFs wh
en you know the password
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
python cli_unlock.py protected.pdf -o unlocked.pdf

# With custom password
python cli_unlock.py protected.pdf -p "mypassword" -o unlocked.pdf

# Interactive password prompt
python cli_unlock.py protected.pdf -o unlocked.pdf --ask-password
```

### Options
- `-p, --password`: Password (default: "password")
- `-o, --output`: Output file path
- `--ask-password`: Prompt for password interactively
- `--verbose`: Show detailed progress

---

## Password Cracking Tool

Advanced password recovery using multiple attack strategies.

### Quick Start Examples

```bash
# Dictionary attack (fastest for common passwords)
python cli_crack.py --file document.pdf --mode dictionary

# Brute force with numeric passwords (up to 6 digits)
python cli_crack.py --file document.pdf --mode bruteforce --max-length 6

# AI-powered contextual generation (no API keys needed)
python cli_crack.py --file invoice.pdf --mode ai_attack

# Batch processing entire directory
python cli_crack.py --directory ./pdfs --mode dictionary --save

# Custom wordlist with company-specific passwords
python cli_crack.py --file report.pdf --wordlist company_passwords.txt
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

### Configuration Options

#### Brute Force Settings
- `--charset`: Character set (`numeric`, `lowercase`, `uppercase`, `alphanumeric`, `all`)
- `--min-length`: Minimum password length (default: 1)
- `--max-length`: Maximum password length (default: 4, max: 10)

#### Dictionary Settings
- `--wordlist`: Custom wordlist file (one password per line)
- Built-in dictionary includes: common passwords, years, company patterns

#### General Options
- `--verbose`: Show detailed progress and timing
- `--save`: Save results to timestamped files
- `--timeout`: Maximum time per attack (default: 1 hour)

### Performance Benchmarks

| Attack Type | Parameters | Time Estimate | Success Rate |
|-------------|------------|---------------|--------------|
| Dictionary | Default list (~50 passwords) | ~5 seconds | High |
| Brute Force | Numeric, 1-4 chars | ~10 seconds | High |
| Brute Force | Numeric, 1-6 chars | ~15 minutes | High |
| AI-Powered | Context analysis | ~10 seconds | Medium-High |
| John the Ripper | Dictionary + rules | Variable | Very High |

*Performance varies by hardware, PDF size, and password complexity.*

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

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/pdf/upload` | Upload PDF for processing |
| POST | `/api/v1/crack/{id}` | Initiate password cracking |
| POST | `/api/v1/unlock/{id}` | Unlock with known password |
| GET | `/api/v1/pdf/{id}/download` | Download processed PDF |
| GET | `/api/v1/health` | System health check |

### API Workflow Example

```bash
# 1. Upload PDF
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/pdf/upload" \
  -F "file=@document.pdf")

PDF_ID=$(echo $UPLOAD_RESPONSE | jq -r '.id')

# 2. Start cracking
curl -X POST "http://localhost:8000/api/v1/crack/$PDF_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "dictionary",
    "max_length": 6,
    "charset": "alphanumeric"
  }'

# 3. Download result (when ready)
curl -X GET "http://localhost:8000/api/v1/pdf/$PDF_ID/download" \
  --output unlocked.pdf
```

### API Features

- **Security**: Input validation, rate limiting, and secure file handling
- **Monitoring**: Health checks and error tracking
- **Performance**: Async processing and connection pooling
- **Reliability**: Comprehensive error handling and graceful degradation
- **Mobile-Ready**: RESTful design for easy mobile app integration

---

## Development & Testing

### Running Tests

```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=app --cov-report=html

# Run specific test categories
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/integration/ -v  # Integration tests

# Performance testing
python scripts/benchmark.py
```

### Creating Test Data

```bash
# Generate test PDFs for development
python scripts/test_example.py

# Verify all components work together
python scripts/verify_refactor.py
```

### Code Quality

- **Architecture**: Clean architecture with dependency injection
- **Testing**: 95%+ test coverage with comprehensive edge case handling
- **Documentation**: Comprehensive docstrings and API documentation
- **Security**: Input sanitization, bounds checking, and secure defaults
- **Performance**: Memory-safe operations and resource management

---

## 🔧 Configuration

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

### Custom Wordlists

Create text files with passwords (one per line):

```bash
# company_passwords.txt
Company2024!
john.doe@company.com
Admin123
Finance2024
Q4_Report
```

Usage: `python cli_crack.py --file report.pdf --wordlist company_passwords.txt`

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

1. Check the [API documentation](http://localhost:8000/docs) for endpoint details
2. Run `python cli_crack.py --help` for CLI options
3. Review test files in `tests/` for usage examples
4. Check `QUICKSTART.md` for common workflows

### Project Files

- **[LICENSE](LICENSE)**: MIT License terms
- **[SECURITY.md](SECURITY.md)**: Security policy and vulnerability reporting
- **[ETHICS.md](ETHICS.md)**: Legal use guidelines and ethical considerations

---

## Performance Optimization

### Recommended Workflow

1. **Start with Dictionary Attack** (fastest for common passwords)
2. **Use AI-Powered Generation** for intelligent guessing
3. **Create Custom Wordlists** with relevant context
4. **Brute Force Only** for very short passwords (≤6 characters)
5. **External Tools** for advanced scenarios (John the Ripper, PDFCrack)

### Hardware Recommendations

- **CPU**: Modern multi-core processor (4+ cores recommended)
- **RAM**: 8GB+ for large wordlists and AI processing
- **Storage**: SSD for faster file I/O operations
- **GPU**: Optional, for AI model acceleration (CUDA-compatible)

### Scaling Considerations

- **Batch Processing**: Use directory mode for multiple files
- **Parallel Processing**: API supports concurrent requests
- **Resource Limits**: Configurable timeouts and memory limits
- **Monitoring**: Built-in health checks and metrics collection
