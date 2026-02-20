#!/usr/bin/env python3
"""
Quick syntax and import check before running uvicorn.
Run: python check.py
"""
import sys
import py_compile
from pathlib import Path

def check_file(file_path: Path) -> bool:
    """Check a single Python file for syntax errors."""
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error in {file_path}:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking {file_path}:")
        print(f"   {e}")
        return False

def check_imports() -> bool:
    """Try importing main modules to catch import errors."""
    try:
        import app.main
        import app.api.routes_chat
        import app.core.config
        import app.core.logging
        import app.core.rate_limit
        import app.services.llm.openai_provider
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during import: {e}")
        return False

def main():
    """Check all Python files in the app directory."""
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / "app"
    
    if not app_dir.exists():
        print(f"❌ App directory not found: {app_dir}")
        sys.exit(1)
    
    print("Checking Python files...")
    all_ok = True
    
    # Check all Python files
    for py_file in app_dir.rglob("*.py"):
        if not check_file(py_file):
            all_ok = False
    
    if not all_ok:
        print("\n❌ Some files have syntax errors")
        sys.exit(1)
    
    print("✅ All files have valid syntax")
    
    # Try imports
    print("\nChecking imports...")
    if not check_imports():
        print("\n❌ Import check failed")
        sys.exit(1)
    
    print("\n✅ All checks passed! Safe to run uvicorn.")

if __name__ == "__main__":
    main()
