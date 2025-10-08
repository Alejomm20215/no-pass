#!/usr/bin/env python3
"""
Quick verification script to ensure refactor is working

This script verifies that all modules can be imported and basic functionality works.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules can be imported"""
    print("[*] Testing imports...")
    
    try:
        # Core domain
        from app.core.domain import entities, constants
        print("  [OK] Core domain imports OK")
        
        # Core interfaces
        from app.core.interfaces import pdf_handler, attack_strategy, wordlist_provider
        print("  [OK] Core interfaces imports OK")
        
        # Core use cases
        from app.core.use_cases import crack_password, unlock_pdf, batch_process
        print("  [OK] Core use cases imports OK")
        
        # Adapters
        from app.adapters.repositories import pdf_handler as pdf_impl, wordlist_provider as wl_impl
        from app.adapters.strategies import dictionary_attack, bruteforce_attack, hybrid_attack
        print("  [OK] Adapters imports OK")
        
        # API
        from app.api.v1.routes import health, pdf, crack
        from app.api.v1.schemas import crack as crack_schema, pdf as pdf_schema, response
        print("  [OK] API imports OK")
        
        # Config
        from app.config import settings, dependencies
        print("  [OK] Config imports OK")
        
        # Main app
        from app import main
        print("  [OK] Main app imports OK")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_domain_models():
    """Test domain models creation"""
    print("\n[*] Testing domain models...")
    
    try:
        from app.core.domain.entities import (
            PDFDocument, CrackJob, AttackOptions, CrackResult,
            AttackMode, CharsetType
        )
        
        # Create PDF document
        pdf = PDFDocument(filename="test.pdf", size=1024, is_protected=True)
        assert pdf.filename == "test.pdf"
        print("  [OK] PDFDocument creation OK")
        
        # Create attack options
        options = AttackOptions(
            mode=AttackMode.DICTIONARY,
            charset=CharsetType.NUMERIC
        )
        assert options.mode == AttackMode.DICTIONARY
        print("  [OK] AttackOptions creation OK")
        
        # Create crack job
        job = CrackJob(pdf_id="test123")
        job.start()
        assert job.started_at is not None
        print("  [OK] CrackJob creation OK")
        
        # Create result
        result = CrackResult(success=True, password="123456", attempts=10)
        assert result.success == True
        print("  [OK] CrackResult creation OK")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Domain model error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Test dependency injection"""
    print("\n[*] Testing dependency injection...")
    
    try:
        from app.config.dependencies import (
            get_pdf_handler,
            get_wordlist_provider,
            get_crack_password_use_case,
            get_unlock_pdf_use_case
        )
        
        # Get handlers
        pdf_handler = get_pdf_handler()
        print(f"  [OK] PDF Handler: {type(pdf_handler).__name__}")
        
        wordlist_provider = get_wordlist_provider()
        print(f"  [OK] Wordlist Provider: {type(wordlist_provider).__name__}")
        
        # Get use cases
        crack_use_case = get_crack_password_use_case()
        print(f"  [OK] Crack Use Case: {type(crack_use_case).__name__}")
        
        unlock_use_case = get_unlock_pdf_use_case()
        print(f"  [OK] Unlock Use Case: {type(unlock_use_case).__name__}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Dependency injection error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wordlist_provider():
    """Test wordlist provider"""
    print("\n[*] Testing wordlist provider...")
    
    try:
        from app.config.dependencies import get_wordlist_provider
        
        provider = get_wordlist_provider()
        wordlist = provider.get_default_wordlist()
        
        assert len(wordlist) > 0
        assert "123456" in wordlist
        assert "password" in wordlist
        
        print(f"  [OK] Default wordlist loaded: {len(wordlist)} passwords")
        return True
    except Exception as e:
        print(f"  [ERROR] Wordlist provider error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_creation():
    """Test FastAPI app creation"""
    print("\n[*] Testing FastAPI app creation...")
    
    try:
        from app.main import app
        
        assert app is not None
        print(f"  [OK] FastAPI app created")
        print(f"  [INFO] App title: {app.title}")
        print(f"  [INFO] App version: {app.version}")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print(f"  [INFO] Total routes: {len(routes)}")
        
        # Check key routes exist
        api_routes = [r for r in routes if r.startswith('/api/v1')]
        print(f"  [INFO] API routes: {len(api_routes)}")
        
        assert '/api/v1/health' in routes
        assert any('/pdf/upload' in r for r in routes)
        assert any('/crack/' in r for r in routes)
        
        print(f"  [OK] All key routes present")
        
        return True
    except Exception as e:
        print(f"  [ERROR] API creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("="*60)
    print("REFACTOR VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Domain Models", test_domain_models()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Wordlist Provider", test_wordlist_provider()))
    results.append(("API Creation", test_api_creation()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All verification tests passed!")
        print("\nRefactor is successful! The new architecture is working.")
        print("\nNext steps:")
        print("  1. Run the API server: python app/main.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Test CLI: python cli_crack.py --help")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

