#!/usr/bin/env python3
"""
remove_password_pikepdf.py

Remove the password from a PDF using pikepdf.
For security, the default password here is the one I gave 
(consider changing it or not leaving it in shared files).

By default, the password is default_password.

Usage:
  python remove_password_pikepdf.py protected_file.pdf -o output.pdf
  # or overwrite the default password:
  python remove_password_pikepdf.py protected_file.pdf -p "another_password" -o output.pdf
"""
import argparse
import sys
from pathlib import Path

try:
    import pikepdf
except Exception as e:
    print("This script requires 'pikepdf'. Install it with: pip install pikepdf", file=sys.stderr)
    raise

DEFAULT_PASSWORD = "default_password"

def remove_password(input_path: Path, output_path: Path, password: str):
    try:
        # Try opening using the password (if no password, pikepdf.open will work without password)
        pdf = pikepdf.open(str(input_path), password=password) if password else pikepdf.open(str(input_path))
        # Save copy without encryption
        pdf.save(str(output_path))
        pdf.close()
        print(f"Saved without password to: {output_path}")
    except pikepdf._qpdf.PasswordError:
        print("Incorrect password.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

def main():
    parser = argparse.ArgumentParser(description="Remove password from a PDF (uses pikepdf).")
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("-o", "--output", help="Path to the output PDF file (default adds _no_pass.pdf)", default=None)
    parser.add_argument("-p", "--password", help="Password for the PDF (default provided)", default=DEFAULT_PASSWORD)
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print("The input file does not exist.", file=sys.stderr)
        sys.exit(1)

    out = Path(args.output) if args.output else inp.with_name(inp.stem + "_no_pass.pdf")

    if out.resolve() == inp.resolve():
        print("The output path cannot be the same as the input path. Choose another.", file=sys.stderr)
        sys.exit(4)

    remove_password(inp, out, args.password)

if __name__ == "__main__":
    main()
