#!/usr/bin/env python3
"""
CLI wrapper for PDF unlocking (backward compatibility)

Usage:
    python cli_unlock.py protected.pdf -p "password" -o unlocked.pdf
"""

import argparse
import sys
from pathlib import Path

from app.config.dependencies import get_unlock_pdf_use_case


def main():
    parser = argparse.ArgumentParser(description="Remove password from a PDF")

    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output PDF file (default adds _unlocked.pdf)",
        default=None,
    )
    parser.add_argument("-p", "--password", help="Password for the PDF", required=True)

    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print("The input file does not exist.", file=sys.stderr)
        sys.exit(1)

    out = (
        Path(args.output) if args.output else inp.with_name(inp.stem + "_unlocked.pdf")
    )

    if out.resolve() == inp.resolve():
        print(
            "The output path cannot be the same as the input path. Choose another.",
            file=sys.stderr,
        )
        sys.exit(4)

    # Get use case
    unlock_use_case = get_unlock_pdf_use_case()

    # Execute unlock
    result = unlock_use_case.execute(inp, args.password, out)

    if result.success:
        print(f"[SUCCESS] Saved without password to: {result.unlocked_path}")
    else:
        print(f"[ERROR] Error: {result.error}", file=sys.stderr)
        if "password" in result.error.lower():
            sys.exit(2)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
