from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging
from typing import List
from database import db
from email_service import EmailService
from models import EmailJob, EmailSendResult

logger = logging.getLogger(__name__)


class EmailScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.email_service = EmailService()
        self.is_running = False

    async def start(self):
        """Start the scheduler."""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Email scheduler started")
            
            # Schedule the email checking job to run every minute
            self.scheduler.add_job(
                self.check_and_send_emails,
                IntervalTrigger(minutes=1),
                id='email_checker',
                replace_existing=True
            )

    async def stop(self):
        """Stop the scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Email scheduler stopped")

    async def check_and_send_emails(self):
        """Check for due emails and send them."""
        try:
            # Get all due email jobs
            due_jobs = await db.get_due_email_jobs()
            
            if not due_jobs:
                logger.debug("No due emails to send")
                return
            
            logger.info(f"Found {len(due_jobs)} due emails to send")
            
            for job in due_jobs:
                await self.send_single_email(job)
                
        except Exception as e:
            logger.error(f"Error in check_and_send_emails: {e}")

    async def send_single_email(self, job: EmailJob):
        """Send a single email job."""
        try:
            # Get user information to get access tokens
            from auth import db as auth_db  # Import here to avoid circular import
            # job.user_id is the MongoDB _id, not google_id
            user = await auth_db.get_user_by_id(job.user_id)
            
            if not user:
                logger.error(f"User not found for job {job.id}")
                return
            
            # Send the email
            result = await self.email_service.send_email(
                email_job=job,
                user_access_token=user.access_token,
                user_refresh_token=user.refresh_token
            )
            
            if result.success:
                # Update job with sent time and next send time
                sent_time = result.sent_at
                next_send = sent_time + timedelta(days=job.every_n_days)
                
                await db.update_job_sent_time(job.id, sent_time, next_send)
                logger.info(f"Email sent successfully for job {job.id} to {job.recipient}")
            else:
                logger.error(f"Failed to send email for job {job.id}: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Error sending email for job {job.id}: {e}")

    async def schedule_job(self, job: EmailJob):
        """Schedule a new email job."""
        try:
            # Calculate next send time
            now = datetime.utcnow()
            if job.last_sent:
                next_send = job.last_sent + timedelta(days=job.every_n_days)
            else:
                next_send = now + timedelta(days=job.every_n_days)
            
            # Update job with next send time
            await db.update_email_job(
                job.id,
                job.user_id,
                {"next_send": next_send}
            )
            
            logger.info(f"Email job {job.id} scheduled for {next_send}")
            
        except Exception as e:
            logger.error(f"Error scheduling job {job.id}: {e}")

    async def update_job_schedule(self, job_id: str, user_id: str, every_n_days: int):
        """Update the schedule of an existing job."""
        try:
            job = await db.get_email_job(job_id, user_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            # Calculate new next send time
            now = datetime.utcnow()
            if job.last_sent:
                next_send = job.last_sent + timedelta(days=every_n_days)
            else:
                next_send = now + timedelta(days=every_n_days)
            
            # Update job
            await db.update_email_job(
                job_id,
                user_id,
                {
                    "every_n_days": every_n_days,
                    "next_send": next_send
                }
            )
            
            logger.info(f"Job {job_id} schedule updated to every {every_n_days} days")
            
        except Exception as e:
            logger.error(f"Error updating job schedule {job_id}: {e}")

    async def pause_job(self, job_id: str, user_id: str):
        """Pause an email job."""
        try:
            await db.update_email_job(
                job_id,
                user_id,
                {"status": "paused"}
            )
            logger.info(f"Job {job_id} paused")
            
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")

    async def resume_job(self, job_id: str, user_id: str):
        """Resume a paused email job."""
        try:
            job = await db.get_email_job(job_id, user_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            # Calculate next send time
            now = datetime.utcnow()
            if job.last_sent:
                next_send = job.last_sent + timedelta(days=job.every_n_days)
            else:
                next_send = now + timedelta(days=job.every_n_days)
            
            await db.update_email_job(
                job_id,
                user_id,
                {
                    "status": "active",
                    "next_send": next_send
                }
            )
            
            logger.info(f"Job {job_id} resumed")
            
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")


# Create scheduler instance
email_scheduler = EmailScheduler() 