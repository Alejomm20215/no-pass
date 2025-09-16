## Remove password from a PDF (pikepdf)

A tiny helper script to decrypt a password-protected PDF and save an unencrypted copy using `pikepdf`.

### Requirements
- Python 3.7+
- `pikepdf` Python package

Install `pikepdf`:

```bash
pip install pikepdf
```

### Script
`remove_password_pikepdf.py`

### What it does
- Opens a PDF using the provided password (or no password if not required)
- Writes out a new PDF without encryption

### Usage
```bash
python remove_password_pikepdf.py protected_file.pdf -o output.pdf
```

Override the default password:
```bash
python remove_password_pikepdf.py protected_file.pdf -p "another_password" -o output.pdf
```

If you omit `-o/--output`, the script writes to `<input_stem>_no_pass.pdf` in the same directory.

### Arguments
- `input` (positional): Path to the input PDF file
- `-o, --output` (optional): Output PDF path. Defaults to `<input_stem>_no_pass.pdf`
- `-p, --password` (optional): Password to unlock the PDF. Defaults to the script's `DEFAULT_PASSWORD` value

### Defaults and behavior
- Default password is `default_password` (see `DEFAULT_PASSWORD` in the script)
- The script prevents overwriting the original input: output path must differ from input

### Exit codes
- `1`: Input file does not exist
- `2`: Incorrect password
- `3`: Other unexpected error (see printed message)
- `4`: Output path is the same as input path

### Examples
- Basic decrypt to a specific file
  ```bash
  python remove_password_pikepdf.py report_locked.pdf -o report_unlocked.pdf
  ```
- Provide a password and let the script name the output automatically
  ```bash
  python remove_password_pikepdf.py bank.pdf -p "My$tr0ngPass!"
  # -> bank_no_pass.pdf
  ```

### Windows PowerShell notes
- Quote passwords that include spaces or special characters: `-p "My Pass!"`
- Use full paths if files are in different directories, e.g.: `C:\Users\you\Docs\file.pdf`

### Security notes
- Be mindful of where you store the unlocked PDF
- Consider changing or removing the default password in the script before sharing it
- Passing passwords on the command line may appear in your shell history

### Troubleshooting
- "This script requires 'pikepdf'": install it with `pip install pikepdf`
- "Incorrect password": verify the password and try again with `-p`
- "Output path cannot be the same as the input path": choose a different `-o` value

### Legal/Ethical
Only remove passwords from PDFs that you own or have explicit permission to modify.


