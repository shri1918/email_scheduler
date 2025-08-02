#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the Email Scheduler application setup.
Run this script to check if all dependencies and configurations are correct.
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test Python version."""
    print("Testing Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} is supported")
    return True

def test_dependencies():
    """Test if all required dependencies are available."""
    print("\nTesting dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pymongo',
        'motor',
        'apscheduler',
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
        'jose',
        'pydantic',
        'pydantic_settings',
        'httpx',
        'aiofiles'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  {package}")
        except ImportError:
            print(f"  {package} - NOT FOUND")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    print("All dependencies are available")
    return True

def test_configuration():
    """Test configuration files."""
    print("\nTesting configuration...")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("  .env file not found. Please create one based on env.example")
        print("   cp env.example .env")
        print("   Then edit .env with your configuration")
        return False
    
    print("  .env file exists")
    
    # Check if uploads directory exists
    uploads_dir = Path('uploads')
    if not uploads_dir.exists():
        print("  Creating uploads directory...")
        uploads_dir.mkdir(exist_ok=True)
    
    print("  uploads directory ready")
    return True

def test_imports():
    """Test if all application modules can be imported."""
    print("\nTesting application imports...")
    
    try:
        from config import settings
        print("  config module")
    except Exception as e:
        print(f"  config module: {e}")
        return False
    
    try:
        from models import User, EmailJob
        print("  models module")
    except Exception as e:
        print(f"  models module: {e}")
        return False
    
    try:
        from database import db
        print("  database module")
    except Exception as e:
        print(f"  database module: {e}")
        return False
    
    try:
        from auth import google_oauth2
        print("  auth module")
    except Exception as e:
        print(f"  auth module: {e}")
        return False
    
    try:
        from email_service import EmailService
        print("  email_service module")
    except Exception as e:
        print(f"  email_service module: {e}")
        return False
    
    try:
        from scheduler import email_scheduler
        print("  scheduler module")
    except Exception as e:
        print(f"  scheduler module: {e}")
        return False
    
    try:
        from api import app
        print("  api module")
    except Exception as e:
        print(f"  api module: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("Email Scheduler - Setup Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_dependencies,
        test_configuration,
        test_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Configure your .env file with Google OAuth2 credentials")
        print("2. Start MongoDB")
        print("3. Run: python main.py")
        print("4. Visit: http://localhost:8000/docs")
    else:
        print("Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 