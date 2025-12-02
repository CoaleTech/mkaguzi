#!/usr/bin/env python3
"""
Mkaguzi App Dependencies Installation Script
This script installs Python dependencies for the Mkaguzi Internal Audit Management System
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements"""
    required_version = (3, 10)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        print(f"❌ Error: Python {current_version[0]}.{current_version[1]} detected. "
              f"Python >= {required_version[0]}.{required_version[1]} is required.")
        sys.exit(1)

    print(f"✅ Python {current_version[0]}.{current_version[1]} detected")
    return True

def check_requirements_file():
    """Check if requirements.txt exists"""
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt not found in current directory")
        print("Please run this script from the mkaguzi app directory")
        sys.exit(1)

    print("✅ requirements.txt found")
    return True

def install_dependencies():
    """Install Python dependencies using pip"""
    print("\n📦 Installing Python dependencies...")
    print("This may take a few minutes depending on your internet connection.\n")

    try:
        # Use sys.executable to ensure we use the same Python that runs this script
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)

        print("✅ Dependencies installed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)

def main():
    """Main installation function"""
    print("🚀 Installing Mkaguzi App Dependencies")
    print("======================================")

    # Change to script directory if run from elsewhere
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    check_python_version()
    check_requirements_file()
    install_dependencies()

    print("\n🎉 Mkaguzi App is ready to use!\n")
    print("Next steps:")
    print("1. Run 'bench migrate' to apply any database changes")
    print("2. Start the development server with 'bench start'")
    print("3. Access the application in your browser")

if __name__ == "__main__":
    main()