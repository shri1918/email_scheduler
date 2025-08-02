import base64
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import HTTPException, status
from config import settings
from models import EmailJob, EmailSendResult
from auth import google_oauth2
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/gmail.send']

    def _create_message(self, sender: str, to: str, subject: str, body: str, attachments: List[str] = None) -> dict:
        """Create a Gmail message with optional attachments."""
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        # Add body
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)

        # Add attachments
        if attachments:
            for attachment_path in attachments:
                try:
                    with open(attachment_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment_path.split("/")[-1]}'
                    )
                    message.attach(part)
                except Exception as e:
                    logger.warning(f"Failed to attach file {attachment_path}: {e}")

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    async def _get_valid_credentials(self, user_access_token: str, user_refresh_token: str) -> Credentials:
        """Get valid credentials, refreshing if necessary."""
        credentials = Credentials(
            token=user_access_token,
            refresh_token=user_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=self.scope
        )

        # Check if token is expired
        if credentials.expired:
            try:
                credentials.refresh(Request())
                logger.info("Access token refreshed successfully")
            except Exception as e:
                logger.error(f"Failed to refresh access token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to refresh access token. Please re-authenticate."
                )

        return credentials

    async def send_email(self, email_job: EmailJob, user_access_token: str, user_refresh_token: str) -> EmailSendResult:
        """Send an email using Gmail API."""
        try:
            # Get valid credentials
            credentials = await self._get_valid_credentials(user_access_token, user_refresh_token)
            
            # Build Gmail service
            service = build('gmail', 'v1', credentials=credentials)
            
            # Get user's email address
            user_info = await google_oauth2.get_user_info(credentials.token)
            sender_email = user_info['email']
            
            # Create message
            message = self._create_message(
                sender=sender_email,
                to=email_job.recipient,
                subject=email_job.subject,
                body=email_job.body,
                attachments=email_job.attachments
            )
            
            # Send email
            sent_message = service.users().messages().send(userId='me', body=message).execute()
            
            sent_time = datetime.utcnow()
            next_send = sent_time + timedelta(days=email_job.every_n_days)
            
            return EmailSendResult(
                job_id=email_job.id,
                recipient=email_job.recipient,
                subject=email_job.subject,
                sent_at=sent_time,
                success=True
            )
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return EmailSendResult(
                job_id=email_job.id,
                recipient=email_job.recipient,
                subject=email_job.subject,
                sent_at=datetime.utcnow(),
                success=False,
                error_message=str(error)
            )
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return EmailSendResult(
                job_id=email_job.id,
                recipient=email_job.recipient,
                subject=email_job.subject,
                sent_at=datetime.utcnow(),
                success=False,
                error_message=str(e)
            )

    async def test_email_connection(self, access_token: str, refresh_token: str) -> bool:
        """Test if the user's Gmail connection is working."""
        try:
            credentials = await self._get_valid_credentials(access_token, refresh_token)
            service = build('gmail', 'v1', credentials=credentials)
            
            # Try to get user profile to test connection
            profile = service.users().getProfile(userId='me').execute()
            return True
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False 