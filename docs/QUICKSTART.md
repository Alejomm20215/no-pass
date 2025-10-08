# PDF Password Tools - Quick Start

## Installation
```bash
pip install pikepdf
```

---

## Common Use Cases

### Know the password → Unlock
```bash
python scripts/cli_unlock.py protected.pdf -p "password" -o unlocked.pdf
```

### Don't know password → Crack it
```bash
# Try common passwords (fastest)
python scripts/cli_crack.py --file protected.pdf --mode dictionary

# Custom wordlist
python scripts/cli_crack.py --file protected.pdf --wordlist custom.txt

# Numeric brute force (short passwords)
python scripts/cli_crack.py --file protected.pdf --mode bruteforce --max-length 6
```

### Process multiple PDFs
```bash
python scripts/cli_crack.py --directory ./pdfs --mode dictionary --save
```

---

## Key Commands

| Command | Description |
|---------|-------------|
| `scripts/cli_unlock.py` | Remove password (if known) |
| `scripts/cli_crack.py --mode dictionary` | Try common passwords |
| `scripts/cli_crack.py --mode bruteforce` | Generate combinations |
| `scripts/cli_crack.py --mode john` | Use John the Ripper |
| `scripts/cli_crack.py --mode pdfcrack` | Use PDFCrack |
| `scripts/cli_crack.py --directory` | Process folder of PDFs |

---

## Workflow

1. **Dictionary first** (fastest)
2. **Custom wordlist** (contextual)
3. **Brute force** (only for short passwords ≤6 chars)

---

## Key Options

| Option | Description | Example |
|--------|-------------|---------|
| `--mode dictionary` | Common passwords | Default |
| `--mode bruteforce` | All combinations | Short passwords |
| `--max-length N` | Max password length | `--max-length 6` |
| `--wordlist file` | Custom dictionary | `--wordlist custom.txt` |
| `--save` | Save results | `--save` |
| `--verbose` | Show progress | `--verbose` |

---

## Performance

| Attack | Time | Notes |
|--------|------|-------|
| Dictionary | ~5 sec | 50 common passwords |
| Brute force (1-4) | ~10 sec | 11,110 combinations |
| Brute force (1-6) | ~15 min | 1M+ combinations |

---

## Common Issues

**"Requires pikepdf"**: `pip install pikepdf`
**"Too slow"**: Use `--max-length 4` or `--charset numeric`
**"Not found"**: Create custom wordlist with relevant names/dates

---

## 30-Second Start

```bash
pip install pikepdf
python scripts/cli_crack.py --directory ./your_pdfs --save
# Check results in passwords_found.txt
```

---

## 📚 More Info

See `README.md` for complete documentation.

**Ethics**: Only use on PDFs you own or have permission to access.

