#!/usr/bin/env python3
"""
Test script to manually trigger the scheduler and debug email sending
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from scheduler import email_scheduler
from models import EmailJob

async def test_scheduler():
    """Test the scheduler functionality."""
    print("🔍 Testing Email Scheduler...")
    
    # Connect to database
    await db.connect_to_mongo()
    
    try:
        # Get all due jobs
        print("1. Checking for due jobs...")
        due_jobs = await db.get_due_email_jobs()
        print(f"✅ Found {len(due_jobs)} due jobs")
        
        for job in due_jobs:
            print(f"   - Job {job.id}: {job.recipient} (every {job.every_n_days} days)")
            print(f"     Status: {job.status}")
            print(f"     Next send: {job.next_send}")
            print(f"     Last sent: {job.last_sent}")
        
        # Get all active jobs
        print("\n2. Checking all active jobs...")
        all_jobs = await db.db.email_jobs.find({"status": "active"}).to_list(length=100)
        print(f"✅ Found {len(all_jobs)} active jobs")
        
        for job_dict in all_jobs:
            print(f"   - Job {job_dict['_id']}: {job_dict.get('recipient')}")
            print(f"     Next send: {job_dict.get('next_send')}")
            print(f"     Every N days: {job_dict.get('every_n_days')}")
        
        # Manually trigger scheduler
        print("\n3. Manually triggering scheduler...")
        await email_scheduler.check_and_send_emails()
        print("✅ Scheduler check completed")
        
        # Check again for due jobs
        print("\n4. Checking for due jobs after scheduler run...")
        due_jobs_after = await db.get_due_email_jobs()
        print(f"✅ Found {len(due_jobs_after)} due jobs after scheduler run")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_scheduler()) 