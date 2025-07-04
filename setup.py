"""
Setup script for the Tribology Experiment User Interface
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ["experiment_data", "logs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    """Main setup function."""
    print("=" * 50)
    print("Tribology Experiment Setup")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if install_requirements():
        print("\nSetup completed successfully!")
        print("\nTo run the application:")
        print("python UI_experimento_livre_main.py")
    else:
        print("\nSetup failed. Please check the error messages above.")
        
    print("\nPress Enter to continue...")
    input()

if __name__ == "__main__":
    main()
