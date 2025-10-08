# PDF Password Tools

Set of tools for working with password-protected PDFs using `pikepdf`.

## Tools Included

### CLI Tools (Main Entry Points)
1. **`cli_unlock.py`** - Remove password protection when you know the password
2. **`cli_crack.py`** - Crack passwords using dictionary/brute force/John the Ripper/PDFCrack

### API Backend (Mobile App Ready)
3. **`app/main.py`** - FastAPI server for mobile integration
4. **API endpoints** - REST API for password cracking and PDF management

### Utility Scripts
5. **`scripts/test_example.py`** - Create test PDFs for development
6. **`scripts/verify_refactor.py`** - Verify the new architecture works correctly

---

## 1. Remove Password (pikepdf)

Tool to decrypt a password-protected PDF when you already know the password.

### Requirements
- Python 3.7+
- `pikepdf` package: `pip install pikepdf`

### Usage
```bash
python remove_password_pikepdf.py protected_file.pdf -o output.pdf
```

With custom password:
```bash
python remove_password_pikepdf.py protected_file.pdf -p "mypassword" -o unlocked.pdf
```

### Arguments
- `input`: Input PDF file
- `-o, --output`: Output file (default: `<input>_no_pass.pdf`)
- `-p, --password`: Password (default: `default_password`)

### Examples
```bash
python remove_password_pikepdf.py report.pdf -o unlocked.pdf
python remove_password_pikepdf.py bank.pdf -p "MyPass!"
```

**Note**: Only unlock PDFs you own or have permission to modify.

---

## 🚀 API Usage (FastAPI Backend)

The new architecture includes a FastAPI backend for mobile app integration.

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python app/main.py
# Visit: http://localhost:8000/docs
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/pdf/upload` | Upload PDF file |
| POST | `/api/v1/crack/{pdf_id}` | Crack password |
| POST | `/api/v1/crack/{pdf_id}/unlock` | Unlock with known password |
| GET | `/api/v1/pdf/{pdf_id}/download` | Download unlocked PDF |
| GET | `/api/v1/health` | Health check |

### Example API Usage

```bash
# Upload PDF
curl -X POST "http://localhost:8000/api/v1/pdf/upload" \
  -F "file=@document.pdf"

# Crack password
curl -X POST "http://localhost:8000/api/v1/crack/12345678-1234-1234-1234-123456789012" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "dictionary",
    "max_length": 6
  }'

# Download unlocked
curl -X GET "http://localhost:8000/api/v1/pdf/12345678-1234-1234-1234-123456789012/download" \
  --output unlocked.pdf
```

### Architecture Benefits

- **Clean Architecture**: Easy to test, extend, and maintain
- **Dependency Injection**: Loosely coupled components
- **Multiple Attack Methods**: Dictionary, brute force, John the Ripper, PDFCrack
- **Mobile Ready**: FastAPI REST API for app integration
- **Scalable**: Can add database, caching, async processing

### Advanced Attack Methods

The new architecture supports external tools for enhanced cracking:

- **John the Ripper**: Professional password cracking framework
- **PDFCrack**: PDF-specialized cracking tool
- **Custom binaries**: Specify paths to your own installations

Usage:
```bash
# John the Ripper
python cli_crack.py --file protected.pdf --mode john --john-binary /usr/bin/john

# PDFCrack
python cli_crack.py --file protected.pdf --mode pdfcrack --pdfcrack-binary /usr/bin/pdfcrack
```

---

## 2. Password Cracker

Advanced tool to **recover passwords from protected PDFs** when you don't know the password. Uses multiple attack strategies.

### Requirements
- Python 3.7+
- `pikepdf` package: `pip install pikepdf`

### Basic Usage

#### Single file - dictionary attack
```bash
python cli_crack.py --file protected.pdf --mode dictionary
```

#### Directory - batch processing
```bash
python cli_crack.py --directory ./pdfs --mode dictionary
```

#### Brute force - numeric passwords (fast)
```bash
python cli_crack.py --file doc.pdf --mode bruteforce --max-length 6
```

#### Custom wordlist
```bash
python cli_crack.py --directory ./pdfs --wordlist my_passwords.txt
```

#### Combined attack (dictionary + brute force)
```bash
python cli_crack.py --file doc.pdf --mode both
```

### Attack Modes
- `dictionary`: Try common passwords (default)
- `bruteforce`: Generate all combinations
- `both`: Dictionary first, then brute force

### Brute Force Options
- `--charset`: `numeric`, `lowercase`, `uppercase`, `alphanumeric`, `all`
- `--min-length`: Minimum password length (default: 1)
- `--max-length`: Maximum password length (default: 4)

### Other Options
- `--verbose`: Show detailed progress
- `--save`: Save results to file

### Built-in Dictionary
Includes 50+ common passwords:
- Numeric: `123456`, `123456789`, etc.
- Alphabetic: `password`, `admin`, etc.
- Combinations: `password123`, `admin123`, etc.
- International: `contraseña`, `administrador`, etc.
- Years: `2020`, `2021`, `2022`, `2023`, `2024`, `2025`

### Custom Wordlist
Create a text file with one password per line:
```
Company2024
john.doe
password123
admin2024
```

Then use: `python pdf_password_cracker.py --file doc.pdf --wordlist custom.txt`

### Performance Guide

| Attack Type | Length | Time Estimate* |
|-------------|---------|---------------|
| Numeric | 1-4 | ~10 seconds |
| Numeric | 1-6 | ~15 minutes |
| Alphanumeric | 1-3 | ~45 seconds |
| Alphanumeric | 1-4 | ~30 minutes |

*Times vary by hardware and PDF size

### Workflow

1. **Dictionary attack first** (fastest for common passwords)
2. **Create custom wordlist** with relevant names/dates if needed
3. **Brute force only** for short passwords (≤6 characters)

### Security & Ethics

⚠️ **Important**:
- Only use on PDFs you own or have explicit permission
- Delete result files after use
- Don't run as administrator/root
- Review PDFs after unlocking

### Troubleshooting

**"Requires pikepdf"**: `pip install pikepdf`
**"No PDFs found"**: Check directory path and file extensions
**"Not password protected"**: PDF has no opening password
**"Brute force too slow"**: Reduce `--max-length` or use `--charset numeric`

### Integration

Found passwords can be used with the unlock tool:
```bash
python remove_password_pikepdf.py protected.pdf -p "123456" -o unlocked.pdf
```
