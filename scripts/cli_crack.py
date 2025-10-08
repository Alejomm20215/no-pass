#!/usr/bin/env python3
"""
CLI wrapper for password cracking (backward compatibility)

Usage:
    python cli_crack.py --file document.pdf --mode dictionary
    python cli_crack.py --directory ./pdfs --mode bruteforce --max-length 6
"""

import argparse
import sys
import logging
from pathlib import Path

from app.config.dependencies import (
    get_pdf_handler,
    get_wordlist_provider,
    get_crack_password_use_case
)
from app.core.domain.entities import AttackOptions, AttackMode, CharsetType
from app.core.domain.constants import CHARSET_MAP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Recover passwords from protected PDFs using dictionary and/or brute force.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_crack.py --file document.pdf --mode dictionary
  python cli_crack.py --directory ./pdfs --mode bruteforce --max-length 6
  python cli_crack.py --file protected.pdf --mode john --john-binary /usr/bin/john
        """
    )

    parser.add_argument('--version', action='version', version='1.0.0')
    
    # Input
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--file', '-f', type=str, help='Individual PDF file to process')
    input_group.add_argument('--directory', '-d', type=str, help='Directory with PDF files')
    
    # Attack mode
    parser.add_argument(
        '--mode', '-m',
        choices=['dictionary', 'bruteforce', 'both', 'john', 'pdfcrack'],
        default='dictionary',
        help='Attack method (default: dictionary)'
    )
    
    # Dictionary options
    parser.add_argument(
        '--wordlist', '-w',
        type=str,
        help='Custom dictionary file (one password per line)'
    )
    
    # Brute force options
    parser.add_argument(
        '--charset',
        choices=['numeric', 'lowercase', 'uppercase', 'alphanumeric', 'all'],
        default='numeric',
        help='Character set for brute force (default: numeric)'
    )
    parser.add_argument(
        '--min-length',
        type=int,
        default=1,
        help='Minimum length for brute force (default: 1)'
    )
    parser.add_argument(
        '--max-length',
        type=int,
        default=4,
        help='Maximum length for brute force (default: 4)'
    )
    
    # General options
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed progress')
    parser.add_argument('--save', '-s', action='store_true', help='Save results to file')
    parser.add_argument('--wordlist-file', type=str, help='Path to wordlist file')
    parser.add_argument('--john-binary', type=str, default='john', help='Path to John the Ripper binary')
    parser.add_argument('--pdf2john-binary', type=str, default='pdf2john.pl', help='Path to pdf2john.pl script')
    parser.add_argument('--pdfcrack-binary', type=str, default='pdfcrack', help='Path to pdfcrack binary')
    
    args = parser.parse_args()
    
    # Get dependencies
    pdf_handler = get_pdf_handler()
    wordlist_provider = get_wordlist_provider()
    crack_use_case = get_crack_password_use_case()
    
    # Load custom wordlist if specified
    custom_wordlist = None
    if args.wordlist:
        wordlist_path = Path(args.wordlist)
        custom_wordlist = wordlist_provider.load_wordlist(wordlist_path)
        if not custom_wordlist:
            print("⚠️  Empty or invalid dictionary, using default dictionary")
    
    # Prepare attack options
    mode_map = {
        'dictionary': AttackMode.DICTIONARY,
        'bruteforce': AttackMode.BRUTEFORCE,
        'both': AttackMode.HYBRID,
        'john': AttackMode.JOHN_RIPPER,
        'pdfcrack': AttackMode.PDFCRACK,
    }
    
    charset_map = {
        'numeric': CharsetType.NUMERIC,
        'lowercase': CharsetType.LOWERCASE,
        'uppercase': CharsetType.UPPERCASE,
        'alphanumeric': CharsetType.ALPHANUMERIC,
        'all': CharsetType.ALL
    }
    
    options = AttackOptions(
        mode=mode_map[args.mode],
        charset=charset_map[args.charset],
        min_length=args.min_length,
        max_length=args.max_length,
        wordlist=custom_wordlist,
        wordlist_file=Path(args.wordlist_file) if args.wordlist_file else None,
        john_binary=args.john_binary,
        pdf2john_binary=args.pdf2john_binary,
        pdfcrack_binary=args.pdfcrack_binary,
        verbose=args.verbose
    )
    
    # Process
    try:
        if args.file:
            # Single file
            pdf_path = Path(args.file)

            if not pdf_path.exists():
                logger.error(f"File not found: {pdf_path}")
                sys.exit(1)

            print(f"\n{'='*60}")
            print(f"Processing: {pdf_path.name}")
            print(f"{'='*60}")

            def progress_callback(progress: float, message: str):
                if args.verbose:
                    print(f"  {progress:.1f}% - {message}")

            logger.info(f"Starting password crack on {pdf_path.name} using {args.mode} mode")
            result = crack_use_case.execute(
                pdf_path,
                options,
                progress_callback if args.verbose else None
            )

            if result.success:
                logger.info(f"Password found for {pdf_path.name}: {result.password}")
                print(f"\n[SUCCESS] Password found")
                print(f"File: {pdf_path.name}")
                print(f"Password: {result.password}")
                print(f"Method: {result.method}")
                print(f"Attempts: {result.attempts}")
                print(f"Duration: {result.duration:.2f}s")

                if args.save:
                    result_file = pdf_path.parent / f"{pdf_path.stem}_password.txt"
                    try:
                        with open(result_file, 'w', encoding='utf-8') as f:
                            f.write(f"Password for {pdf_path.name}: {result.password}\n")
                        print(f"\n[INFO] Password saved to: {result_file}")
                    except Exception as e:
                        logger.warning(f"Could not save result file: {e}")
            else:
                logger.warning(f"Could not find password for {pdf_path.name}")
                print(f"\n[ERROR] Could not recover password")
                print(f"Attempts: {result.attempts}")
                print(f"Duration: {result.duration:.2f}s")
                if result.error:
                    print(f"Error: {result.error}")
                sys.exit(1)
    
        else:
            # Directory - use batch processing
            from app.config.dependencies import get_batch_process_use_case
            batch_use_case = get_batch_process_use_case()

            directory = Path(args.directory)

            if not directory.exists() or not directory.is_dir():
                logger.error(f"Directory not found or not a directory: {directory}")
                sys.exit(1)

            print(f"\nProcessing directory: {directory}")
            print(f"Mode: {args.mode.upper()}")

            logger.info(f"Starting batch processing of {len(list(directory.glob('*.pdf')))} PDF files")
            results = batch_use_case.execute(
                directory,
                options,
                auto_unlock=False,  # Don't auto-unlock in CLI
                keep_originals=True
            )

            # Print summary
            print(f"\n{'='*60}")
            print(f"RESULTS SUMMARY")
            print(f"{'='*60}")

            success_count = sum(1 for r in results.values() if r.get('status') == 'success')
            failed_count = sum(1 for r in results.values() if r.get('status') == 'failed')
            not_protected = sum(1 for r in results.values() if r.get('status') == 'not_protected')

            print(f"Total files: {len(results)}")
            print(f"[SUCCESS] Passwords found: {success_count}")
            print(f"[ERROR] Failed: {failed_count}")
            print(f"[INFO] Not protected: {not_protected}")

            # Print details
            for filename, result in results.items():
                if result.get('status') == 'success':
                    print(f"\n[SUCCESS] {filename}")
                    print(f"   Password: {result['password']}")
                    print(f"   Method: {result['method']}")
                    print(f"   Attempts: {result['attempts']}")
                    print(f"   Duration: {result['duration']:.2f}s")

            # Save results if requested
            if args.save and success_count > 0:
                results_file = directory / "passwords_found.txt"
                try:
                    with open(results_file, 'w', encoding='utf-8') as f:
                        f.write("Found Passwords\n")
                        f.write("="*60 + "\n\n")
                        for filename, result in results.items():
                            if result.get('status') == 'success':
                                f.write(f"{filename}: {result['password']}\n")
                    print(f"\n[INFO] Results saved to: {results_file}")
                except Exception as e:
                    logger.warning(f"Could not save results file: {e}")

            # Exit with appropriate code
            if success_count == 0:
                logger.warning("No passwords were found")
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

