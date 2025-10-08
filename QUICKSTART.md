# PDF Password Tools - Quick Start

## 📦 Installation
```bash
pip install pikepdf
```

---

## 🎯 Common Use Cases

### Know the password → Unlock
```bash
python cli_unlock.py protected.pdf -p "password" -o unlocked.pdf
```

### Don't know password → Crack it
```bash
# AI-powered contextual generation (smartest)
python cli_crack.py --file invoice.pdf --mode ai_attack

# Try common passwords (fast)
python cli_crack.py --file protected.pdf --mode dictionary

# Custom wordlist
python cli_crack.py --file protected.pdf --wordlist custom.txt

# Numeric brute force (short passwords)
python cli_crack.py --file protected.pdf --mode bruteforce --max-length 6
```

### Process multiple PDFs
```bash
python cli_crack.py --directory ./pdfs --mode dictionary --save
```

---

## ⚡ Key Commands

| Command | Description |
|---------|-------------|
| `cli_unlock.py` | Remove password (if known) |
| `cli_crack.py --mode dictionary` | Try common passwords |
| `cli_crack.py --mode bruteforce` | Generate combinations |
| `cli_crack.py --mode ai_attack` | AI-powered contextual generation |
| `cli_crack.py --mode john` | Use John the Ripper |
| `cli_crack.py --mode pdfcrack` | Use PDFCrack |
| `cli_crack.py --directory` | Process folder of PDFs |

---

## 📋 Workflow

1. **AI-powered** (contextually relevant passwords)
2. **Dictionary** (common passwords)
3. **Custom wordlist** (your specific passwords)
4. **Brute force** (only for short passwords ≤6 chars)

---

## 🔧 Key Options

| Option | Description | Example |
|--------|-------------|---------|
| `--mode ai_attack` | AI contextual generation | Smartest first |
| `--mode dictionary` | Common passwords | Fast fallback |
| `--mode bruteforce` | All combinations | Short passwords |
| `--max-length N` | Max password length | `--max-length 6` |
| `--wordlist file` | Custom dictionary | `--wordlist custom.txt` |
| `--save` | Save results | `--save` |
| `--verbose` | Show progress | `--verbose` |

---

## ⚡ Performance

| Attack | Time | Notes |
|--------|------|-------|
| AI-powered | ~10 sec | Contextually relevant passwords (local model) |
| Dictionary | ~5 sec | 50 common passwords |
| Brute force (1-4) | ~10 sec | 11,110 combinations |
| Brute force (1-6) | ~15 min | 1M+ combinations |

---

## 🆘 Common Issues

**"Requires pikepdf"**: `pip install pikepdf`
**"AI not available"**: `pip install transformers torch`
**"Too slow"**: Use `--max-length 4` or `--charset numeric`
**"Not found"**: Create custom wordlist with relevant names/dates

---

## 🚀 30-Second Start

```bash
pip install -r requirements.txt
python cli_crack.py --file invoice.pdf --mode ai_attack
# AI analyzes context and generates smart password candidates
```

---

## 📚 More Info

See `README.md` for complete documentation.

**Ethics**: Only use on PDFs you own or have permission to access.

