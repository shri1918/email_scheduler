#!/usr/bin/env python3
"""
Railway Deployment Check Script
This script helps verify that all required environment variables are set for Railway deployment.
"""

import os
import sys
from urllib.parse import urlparse

def check_environment_variables():
    """Check if all required environment variables are set."""
    required_vars = [
        "MONGODB_URL",
        "MONGODB_DB",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "JWT_SECRET_KEY"
    ]
    
    optional_vars = [
        "GOOGLE_REDIRECT_URI",
        "DEBUG",
        "HOST",
        "PORT",
        "APP_NAME",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "JWT_ALGORITHM",
        "MAX_FILE_SIZE",
        "UPLOAD_DIR"
    ]
    
    print("🔍 Checking Railway deployment configuration...")
    print("=" * 50)
    
    # Check required variables
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_required.append(var)
            print(f"❌ {var}: NOT SET")
        else:
            # Mask sensitive values
            if "SECRET" in var or "PASSWORD" in var or "KEY" in var:
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    print("\n" + "=" * 50)
    
    # Check optional variables
    print("Optional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if not value:
            print(f"⚠️  {var}: NOT SET (using default)")
        else:
            print(f"✅ {var}: {value}")
    
    print("\n" + "=" * 50)
    
    # Validate MongoDB URL
    mongodb_url = os.getenv("MONGODB_URL")
    if mongodb_url:
        try:
            parsed = urlparse(mongodb_url)
            if parsed.scheme in ["mongodb", "mongodb+srv"]:
                print("✅ MongoDB URL format: VALID")
            else:
                print("❌ MongoDB URL format: INVALID (should start with mongodb:// or mongodb+srv://)")
        except Exception as e:
            print(f"❌ MongoDB URL format: INVALID - {e}")
    
    # Check if running on Railway
    if os.getenv("RAILWAY_ENVIRONMENT"):
        print("✅ Running on Railway")
    else:
        print("⚠️  Not running on Railway (local development)")
    
    # Summary
    print("\n" + "=" * 50)
    if missing_required:
        print(f"❌ DEPLOYMENT READY: NO - Missing {len(missing_required)} required variables")
        print("Missing variables:")
        for var in missing_required:
            print(f"  - {var}")
        return False
    else:
        print("✅ DEPLOYMENT READY: YES")
        return True

def main():
    """Main function."""
    success = check_environment_variables()
    
    if not success:
        print("\n📋 To fix deployment issues:")
        print("1. Go to your Railway project dashboard")
        print("2. Navigate to the 'Variables' tab")
        print("3. Add the missing environment variables")
        print("4. Redeploy your application")
        sys.exit(1)
    else:
        print("\n🎉 Your application is ready for Railway deployment!")
        print("Next steps:")
        print("1. Push your code to GitHub")
        print("2. Railway will automatically deploy")
        print("3. Check the deployment logs for any issues")
        print("4. Test your application at your Railway URL")

if __name__ == "__main__":
    main() 