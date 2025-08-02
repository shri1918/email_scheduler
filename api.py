from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from typing import List, Optional
import aiofiles
import os
from datetime import datetime, timedelta
import logging

from config import settings
from models import (
    User, EmailJob, EmailJobCreate, EmailJobUpdate, 
    Token, GoogleAuthResponse, EmailSendResult
)
from database import db
from auth import google_oauth2, create_access_token, get_current_user
from email_service import EmailService
from scheduler import email_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="A SaaS-based recurring email scheduler with Google OAuth2 authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email service instance
email_service = EmailService()


@app.on_event("startup")
async def startup_event():
    """Initialize database connection and start scheduler on startup."""
    try:
        await db.connect_to_mongo()
        await email_scheduler.start()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        # Don't raise the exception to allow the app to start
        # The health check endpoint will indicate if the database is connected


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection and stop scheduler on shutdown."""
    await email_scheduler.stop()
    await db.close_mongo_connection()
    logger.info("Application shutdown successfully")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Email Scheduler API",
        "version": "1.0.0",
        "docs": "/docs",
        "auth_url": "/auth/google"
    }


@app.get("/frontend_example.html")
async def serve_frontend():
    """Serve the frontend HTML file."""
    from fastapi.responses import FileResponse
    return FileResponse("frontend_example.html")


# Authentication endpoints
@app.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth2 authentication."""
    auth_url = google_oauth2.get_authorization_url()
    return {"auth_url": auth_url}


@app.get("/auth/google/callback")
async def google_auth_callback(code: str, state: Optional[str] = None):
    """Handle Google OAuth2 callback."""
    try:
        # Exchange code for tokens
        tokens = await google_oauth2.exchange_code_for_tokens(code)
        
        # Get user info from Google
        user_info = await google_oauth2.get_user_info(tokens["access_token"])
        
        # Check if user exists
        existing_user = await db.get_user_by_google_id(user_info["id"])
        
        if existing_user:
            # Update existing user's tokens
            await db.update_user_tokens(
                existing_user.id,
                tokens["access_token"],
                tokens["refresh_token"],
                datetime.utcnow() + timedelta(hours=1)  # Approximate expiry
            )
            user = existing_user
        else:
            # Create new user
            user = User(
                email=user_info["email"],
                name=user_info["name"],
                google_id=user_info["id"],
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_expiry=datetime.utcnow() + timedelta(hours=1)
            )
            user = await db.create_user(user)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.google_id})
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"http://localhost:8000/frontend_example.html?token={access_token}"
        )
        
    except Exception as e:
        logger.error(f"Google auth callback error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return RedirectResponse(
            url=f"http://localhost:8000/frontend_example.html?error=auth_failed&details={str(e)}"
        )


@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@app.post("/auth/test-connection")
async def test_email_connection(current_user: User = Depends(get_current_user)):
    """Test if the user's Gmail connection is working."""
    try:
        is_valid = await email_service.test_email_connection(
            current_user.access_token,
            current_user.refresh_token
        )
        return {"valid": is_valid}
    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return {"valid": False, "error": str(e)}


# Email job endpoints
@app.post("/jobs", response_model=EmailJob)
async def create_email_job(
    job_data: EmailJobCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new email job."""
    try:
        # Create email job
        email_job = EmailJob(
            user_id=current_user.id,
            recipient=job_data.recipient,
            subject=job_data.subject,
            body=job_data.body,
            attachments=job_data.attachments,
            every_n_days=job_data.every_n_days
        )
        
        # Save to database
        email_job = await db.create_email_job(email_job)
        
        # Schedule the job
        await email_scheduler.schedule_job(email_job)
        
        return email_job
        
    except Exception as e:
        logger.error(f"Error creating email job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create email job"
        )


@app.get("/jobs", response_model=List[EmailJob])
async def get_email_jobs(current_user: User = Depends(get_current_user)):
    """Get all email jobs for the current user."""
    try:
        jobs = await db.get_user_email_jobs(current_user.id)
        return jobs
    except Exception as e:
        logger.error(f"Error getting email jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get email jobs"
        )


@app.get("/jobs/{job_id}", response_model=EmailJob)
async def get_email_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific email job."""
    try:
        job = await db.get_email_job(job_id, current_user.id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email job not found"
            )
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get email job"
        )


@app.put("/jobs/{job_id}", response_model=EmailJob)
async def update_email_job(
    job_id: str,
    job_update: EmailJobUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update an email job."""
    try:
        # Get current job
        current_job = await db.get_email_job(job_id, current_user.id)
        if not current_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email job not found"
            )
        
        # Prepare update data
        update_data = {}
        if job_update.recipient is not None:
            update_data["recipient"] = job_update.recipient
        if job_update.subject is not None:
            update_data["subject"] = job_update.subject
        if job_update.body is not None:
            update_data["body"] = job_update.body
        if job_update.attachments is not None:
            update_data["attachments"] = job_update.attachments
        if job_update.status is not None:
            update_data["status"] = job_update.status
        
        # Update job
        updated_job = await db.update_email_job(job_id, current_user.id, update_data)
        
        # Update schedule if every_n_days changed
        if job_update.every_n_days is not None:
            await email_scheduler.update_job_schedule(job_id, current_user.id, job_update.every_n_days)
        
        # Handle pause/resume
        if job_update.status == "paused":
            await email_scheduler.pause_job(job_id, current_user.id)
        elif job_update.status == "active" and current_job.status == "paused":
            await email_scheduler.resume_job(job_id, current_user.id)
        
        return updated_job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email job"
        )


@app.delete("/jobs/{job_id}")
async def delete_email_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an email job."""
    try:
        success = await db.delete_email_job(job_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email job not found"
            )
        return {"message": "Email job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting email job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete email job"
        )


@app.post("/jobs/{job_id}/pause")
async def pause_email_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Pause an email job."""
    try:
        await email_scheduler.pause_job(job_id, current_user.id)
        return {"message": "Email job paused successfully"}
    except Exception as e:
        logger.error(f"Error pausing email job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause email job"
        )


@app.post("/jobs/{job_id}/resume")
async def resume_email_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resume a paused email job."""
    try:
        await email_scheduler.resume_job(job_id, current_user.id)
        return {"message": "Email job resumed successfully"}
    except Exception as e:
        logger.error(f"Error resuming email job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume email job"
        )


@app.post("/jobs/{job_id}/send-now")
async def send_email_now(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Send an email immediately."""
    try:
        job = await db.get_email_job(job_id, current_user.id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email job not found"
            )
        
        result = await email_service.send_email(
            job,
            current_user.access_token,
            current_user.refresh_token
        )
        
        if result.success:
            # Update job with sent time
            sent_time = result.sent_at
            next_send = sent_time + timedelta(days=job.every_n_days)
            await db.update_job_sent_time(job.id, sent_time, next_send)
            
            return {
                "message": "Email sent successfully",
                "sent_at": result.sent_at.isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {result.error_message}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email now: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


# File upload endpoints
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file for email attachments."""
    try:
        # Check file size
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large"
            )
        
        # Create user-specific upload directory
        user_upload_dir = os.path.join(settings.upload_dir, current_user.id)
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_upload_dir, file.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return {
            "filename": file.filename,
            "file_path": file_path,
            "size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = "unknown"
    try:
        if db.client:
            await db.client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "not_connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "scheduler_running": email_scheduler.is_running,
        "mongodb_url": settings.mongodb_url if settings.debug else "hidden",
        "mongodb_db": settings.mongodb_db
    } 