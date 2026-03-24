#!/usr/bin/env python3
"""
Setup script for Portfolio Scanner
This script helps set up the virtual environment and install dependencies
"""

import subprocess
import sys
import os

def run_command(command, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def main():
    print("🚀 Setting up Portfolio Scanner...")
    
    # Check if Python is available
    python_cmd = None
    for cmd in ['python', 'python3', 'py']:
        success, _, _ = run_command(f"{cmd} --version", check=False)
        if success:
            python_cmd = cmd
            break
    
    if not python_cmd:
        print("❌ Python not found. Please install Python 3.7+ first.")
        return False
    
    print(f"✅ Found Python: {python_cmd}")
    
    # Create virtual environment
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        success, stdout, stderr = run_command(f"{python_cmd} -m venv venv")
        if not success:
            print(f"❌ Failed to create virtual environment: {stderr}")
            return False
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation script path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
        python_path = os.path.join('venv', 'Scripts', 'python')
    else:  # macOS/Linux
        pip_path = os.path.join('venv', 'bin', 'pip')
        python_path = os.path.join('venv', 'bin', 'python')
    
    # Install requirements
    print("📚 Installing dependencies...")
    success, stdout, stderr = run_command(f'"{python_path}" -m pip install --upgrade pip')
    if not success:
        print(f"❌ Failed to upgrade pip: {stderr}")
        return False
    
    success, stdout, stderr = run_command(f'"{python_path}" -m pip install -r requirements.txt')
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    print("✅ Dependencies installed successfully")
    
    print("\n🎉 Setup complete!")
    print("\nTo run the application:")
    if os.name == 'nt':  # Windows
        print("1. venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("1. source venv/bin/activate")
    print("2. streamlit run portfolio_scanner.py")
    print("\nThe app will open at http://localhost:8501")
    
    return True

if __name__ == "__main__":
    main()
