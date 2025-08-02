#!/usr/bin/env python3
"""
MongoDB Connection Test Script
This script tests different MongoDB connection configurations to find one that works on Railway.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongodb_connection(mongodb_url, config_name, config):
    """Test a specific MongoDB connection configuration."""
    try:
        print(f"\n🔍 Testing {config_name}...")
        print(f"URL: {mongodb_url}")
        print(f"Config: {config}")
        
        client = AsyncIOMotorClient(mongodb_url, **config)
        
        # Test connection
        await client.admin.command('ping')
        print(f"✅ {config_name}: SUCCESS")
        
        # Test database access
        db = client["email_scheduler"]
        await db.list_collection_names()
        print(f"✅ {config_name}: Database access successful")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ {config_name}: FAILED - {e}")
        return False

async def main():
    """Main function to test all configurations."""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/email_scheduler?retryWrites=true&w=majority")
    
    print("🚀 Testing MongoDB Connection Configurations")
    print("=" * 60)
    
    # Different connection configurations to test (modern PyMongo syntax)
    configs = {
        "Standard TLS (No Cert Verification)": {
            "tls": True,
            "tlsAllowInvalidCertificates": True,
            "tlsAllowInvalidHostnames": True,
            "retryWrites": True,
            "w": "majority",
            "maxPoolSize": 10,
            "minPoolSize": 1,
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000
        },
        "Minimal TLS": {
            "tls": True,
            "tlsAllowInvalidCertificates": True,
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000
        },
        "Basic Connection": {
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000,
            "retryWrites": True,
            "w": "majority"
        },
        "No TLS": {
            "tls": False,
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000
        }
    }
    
    successful_configs = []
    
    for config_name, config in configs.items():
        success = await test_mongodb_connection(mongodb_url, config_name, config)
        if success:
            successful_configs.append((config_name, config))
    
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    if successful_configs:
        print(f"✅ {len(successful_configs)} configuration(s) worked:")
        for config_name, config in successful_configs:
            print(f"  - {config_name}")
        
        print("\n🎯 RECOMMENDED CONFIGURATION:")
        best_config = successful_configs[0]
        print(f"Use: {best_config[0]}")
        print("Configuration:")
        for key, value in best_config[1].items():
            print(f"  {key}: {value}")
    else:
        print("❌ No configurations worked!")
        print("\n🔧 TROUBLESHOOTING SUGGESTIONS:")
        print("1. Check your MongoDB Atlas network access settings")
        print("2. Verify your MongoDB connection string")
        print("3. Try using a different MongoDB cluster")
        print("4. Check if your IP is whitelisted in MongoDB Atlas")

if __name__ == "__main__":
    asyncio.run(main()) 