#!/usr/bin/env python3
"""
Check job status directly from database
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db

async def check_job():
    """Check the job status."""
    print("🔍 Checking Job Status...")
    
    # Connect to database
    await db.connect_to_mongo()
    
    try:
        # Get the specific job
        from bson import ObjectId
        job_id = "688ceacbb7fc04622e631ae1"
        job_dict = await db.db.email_jobs.find_one({"_id": ObjectId(job_id)})
        
        if job_dict:
            print(f"✅ Job found: {job_dict['_id']}")
            print(f"   Recipient: {job_dict.get('recipient')}")
            print(f"   Status: {job_dict.get('status')}")
            print(f"   Last sent: {job_dict.get('last_sent')}")
            print(f"   Next send: {job_dict.get('next_send')}")
            print(f"   Every N days: {job_dict.get('every_n_days')}")
            print(f"   Created at: {job_dict.get('created_at')}")
            print(f"   Updated at: {job_dict.get('updated_at')}")
        else:
            print("❌ Job not found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_job()) 