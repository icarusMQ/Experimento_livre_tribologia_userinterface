"""
Fix script for setuptools and compatibility issues with Python 3.13
"""

import subprocess
import sys
import os

def fix_setuptools_issue():
    """Fix setuptools import issues."""
    print("Fixing setuptools issues...")
    
    commands = [
        # Force reinstall pip
        [sys.executable, "-m", "pip", "install", "--force-reinstall", "pip"],
        
        # Force reinstall setuptools and wheel
        [sys.executable, "-m", "pip", "install", "--force-reinstall", "setuptools", "wheel"],
        
        # Install build tools
        [sys.executable, "-m", "pip", "install", "--upgrade", "build"],
        
        # Install packaging tools
        [sys.executable, "-m", "pip", "install", "--upgrade", "packaging"],
    ]
    
    for cmd in commands:
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Success")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed: {e}")
            print(f"stderr: {e.stderr}")
            return False
    
    return True

def install_compatible_packages():
    """Install packages with versions compatible with Python 3.13."""
    print("\nInstalling compatible packages...")
    
    # Use direct installation without requirements.txt to avoid dependency conflicts
    packages = [
        "pyserial>=3.5",
        "numpy>=1.24.0", 
        "matplotlib>=3.8.0",
        "pandas>=2.1.0",
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--no-deps",  # Install without dependencies first
                package
            ], check=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
    
    # Now install with dependencies
    print("\nInstalling with dependencies...")
    for package in packages:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                package
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: {package} dependencies may have issues: {e}")

def test_imports():
    """Test if critical packages can be imported."""
    print("\nTesting imports...")
    
    test_packages = [
        "serial",
        "matplotlib",
        "pandas", 
        "numpy",
        "tkinter"
    ]
    
    failed_imports = []
    
    for package in test_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def main():
    """Main fix process."""
    print("=" * 60)
    print("Python 3.13 Compatibility Fix Script")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    # Step 1: Fix setuptools
    if not fix_setuptools_issue():
        print("❌ Failed to fix setuptools issues")
        return 1
    
    # Step 2: Install compatible packages
    install_compatible_packages()
    
    # Step 3: Test imports
    if test_imports():
        print("\n✅ All packages imported successfully!")
        print("\nYou can now try running:")
        print("  python UI_experimento_livre_main.py")
        return 0
    else:
        print("\n❌ Some packages failed to import")
        print("\nTry using Python 3.8-3.11 for better compatibility")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nPress Enter to continue...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
