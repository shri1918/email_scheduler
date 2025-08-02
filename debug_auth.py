#!/usr/bin/env python3
"""
Debug script to test OAuth2 token exchange
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import google_oauth2
from database import db
from models import User
from datetime import datetime, timedelta
from config import settings

async def test_token_exchange(code):
    """Test the token exchange process step by step."""
    print("🔍 Testing OAuth2 token exchange...")
    
    try:
        # Step 1: Exchange code for tokens
        print("1. Exchanging code for tokens...")
        tokens = await google_oauth2.exchange_code_for_tokens(code)
        print(f"✅ Tokens received: {list(tokens.keys())}")
        
        # Step 2: Get user info
        print("2. Getting user info from Google...")
        user_info = await google_oauth2.get_user_info(tokens["access_token"])
        print(f"✅ User info: {user_info['email']} ({user_info['name']})")
        
        # Step 3: Check if user exists
        print("3. Checking if user exists in database...")
        existing_user = await db.get_user_by_google_id(user_info["id"])
        
        if existing_user:
            print("✅ User exists, updating tokens...")
            await db.update_user_tokens(
                existing_user.id,
                tokens["access_token"],
                tokens["refresh_token"],
                datetime.utcnow() + timedelta(hours=1)
            )
            user = existing_user
        else:
            print("✅ Creating new user...")
            user = User(
                email=user_info["email"],
                name=user_info["name"],
                google_id=user_info["id"],
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_expiry=datetime.utcnow() + timedelta(hours=1)
            )
            user = await db.create_user(user)
        
        print(f"✅ User created/updated: {user.email}")
        return user
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_auth.py <authorization_code>")
        sys.exit(1)
    
    code = sys.argv[1]
    
    # Initialize database connection
    async def main():
        await db.connect_to_mongo()
        user = await test_token_exchange(code)
        if user:
            print(f"🎉 Success! User: {user.email}")
        else:
            print("❌ Failed to process authentication")
        await db.close_mongo_connection()
    
    asyncio.run(main()) 