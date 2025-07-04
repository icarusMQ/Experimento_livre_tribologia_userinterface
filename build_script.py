"""
Build script for creating standalone executable using PyInstaller
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

def install_requirements():
    """Install build requirements."""
    print("Installing/updating requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        return False

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    try:
        # Use the spec file for consistent builds
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "tribology_experiment.spec"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

def create_portable_package():
    """Create a portable package with necessary files."""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("Dist directory not found!")
        return False
    
    # Create portable directory
    portable_dir = dist_dir / "TribologyExperiment_Portable"
    portable_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_file = dist_dir / "TribologyExperiment.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, portable_dir)
    
    # Copy configuration and data directories
    files_to_copy = [
        ("config.json", "config.json"),
        ("experiment_data", "experiment_data"),
        ("README.md", "README.md"),
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = portable_dir / dst
        
        if src_path.exists():
            if src_path.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
    
    # Create run script for portable version
    run_script = portable_dir / "run_tribology_experiment.bat"
    with open(run_script, 'w') as f:
        f.write("""@echo off
echo Starting Tribology Experiment...
echo.
TribologyExperiment.exe
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
""")
    
    print(f"Portable package created at: {portable_dir}")
    return True

def main():
    """Main build function."""
    print("=" * 60)
    print("Tribology Experiment - Executable Builder")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("UI_experimento_livre_main.py"):
        print("Error: Main application file not found!")
        print("Make sure you're running this script from the project root directory.")
        return False
    
    # Clean previous builds
    clean_build_dirs()
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Build executable
    if not build_executable():
        return False
    
    # Create portable package
    if not create_portable_package():
        print("Warning: Failed to create portable package, but executable was built successfully.")
    
    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print("Executable location: dist/TribologyExperiment.exe")
    print("Portable package: dist/TribologyExperiment_Portable/")
    print("\nYou can distribute the entire TribologyExperiment_Portable folder")
    print("or just the TribologyExperiment.exe file (standalone).")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nBuild interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)
    
    input("\nPress Enter to continue...")
