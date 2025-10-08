#!/usr/bin/env python3
"""
test_example.py

Example/test script to demonstrate PDF tools.
Creates protected test PDFs so you can test the tools.

Requires: pikepdf
Installation: pip install pikepdf

Usage:
  python test_example.py
  
This will create 5 test PDFs in ./test_pdfs/ with known passwords:
  - test_simple.pdf (password: 123456)
  - test_dict.pdf (password: password)
  - test_custom.pdf (password: Test2024)
  - test_numeric.pdf (password: 5678)
  - test_admin.pdf (password: admin)
"""

import sys
from pathlib import Path

try:
    import pikepdf
except ImportError:
    print("Error: This script requires 'pikepdf'.", file=sys.stderr)
    print("Install it with: pip install pikepdf", file=sys.stderr)
    sys.exit(1)


def create_test_pdf(filename: Path, password: str):
    """Create a password-protected test PDF."""
    try:
        # Create simple PDF
        pdf = pikepdf.Pdf.new()
        
        # Add blank page
        pdf.add_blank_page(page_size=(612, 792))  # Letter size
        
        # Save with password
        pdf.save(filename, encryption=pikepdf.Encryption(
            owner=password,
            user=password
        ))
        
        print(f"[OK] Created: {filename.name} (password: {password})")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating {filename.name}: {e}")
        return False


def main():
    print("="*70)
    print("TEST PDF CREATOR")
    print("="*70)
    print("\nThis script creates protected test PDFs so you can")
    print("test the password recovery tools.\n")

    # Create test directory
    test_dir = Path("./test_pdfs")
    test_dir.mkdir(exist_ok=True)
    print(f"Test directory: {test_dir}\n")

    # Create test PDFs with different passwords
    test_cases = [
        ("test_simple.pdf", "123456", "Simple numeric password"),
        ("test_dict.pdf", "password", "Common dictionary password"),
        ("test_custom.pdf", "Test2024", "Custom password"),
        ("test_numeric.pdf", "5678", "Short numeric password"),
        ("test_admin.pdf", "admin", "Common admin password"),
    ]

    created = 0
    for filename, password, description in test_cases:
        print(f"Creating: {description}")
        filepath = test_dir / filename
        if create_test_pdf(filepath, password):
            created += 1

    print(f"\n{'='*70}")
    print(f"Created {created}/{len(test_cases)} test PDFs")
    print(f"{'='*70}")

    # Instructions
    print("\nHOW TO TEST THE TOOLS:\n")

    print("1. Test dictionary attack:")
    print(f"   python cli_crack.py --directory {test_dir} --mode dictionary --verbose\n")

    print("2. Test numeric brute force:")
    print(f"   python cli_crack.py --file {test_dir}/test_simple.pdf --mode bruteforce --max-length 6\n")

    print("3. Test complete automated process:")
    print(f"   python cli_crack.py --directory {test_dir} --mode both --save\n")

    print("4. Remove password (if you know it):")
    print(f"   python cli_unlock.py {test_dir}/test_simple.pdf -p \"123456\" -o unlocked.pdf\n")

    print("="*70)
    print("TEST PDF PASSWORDS:")
    print("="*70)
    for filename, password, description in test_cases:
        print(f"  • {filename}")
        print(f"    Password: {password} ({description})")

    print("\nNote: These are test PDFs for demonstration.")
    print("    Delete them when you're done testing.\n")


if __name__ == "__main__":
    main()

