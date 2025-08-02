from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from typing import List, Optional
from datetime import datetime
import logging
import asyncio
import ssl
from config import settings
from models import User, EmailJob, EmailJobStatus

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongo(self):
        """Create database connection with retry logic and SSL configuration."""
        max_retries = 3
        retry_delay = 2
        
        # Try different connection configurations (modern PyMongo syntax)
        connection_configs = [
            # Configuration 1: Standard TLS with certificate verification disabled
            {
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
            # Configuration 2: Minimal TLS configuration
            {
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "serverSelectionTimeoutMS": 30000,
                "connectTimeoutMS": 30000,
                "socketTimeoutMS": 30000
            },
            # Configuration 3: Basic connection with timeouts
            {
                "serverSelectionTimeoutMS": 30000,
                "connectTimeoutMS": 30000,
                "socketTimeoutMS": 30000,
                "retryWrites": True,
                "w": "majority"
            },
            # Configuration 4: No TLS (fallback)
            {
                "tls": False,
                "serverSelectionTimeoutMS": 30000,
                "connectTimeoutMS": 30000,
                "socketTimeoutMS": 30000
            }
        ]
        
        # URLs to try (main URL and alternative URL if available)
        urls_to_try = [settings.mongodb_url]
        if settings.mongodb_url_alt:
            urls_to_try.append(settings.mongodb_url_alt)
        
        for attempt in range(max_retries):
            for url_index, mongodb_url in enumerate(urls_to_try):
                for config_index, config in enumerate(connection_configs):
                    try:
                        logger.info(f"Attempting to connect to MongoDB (attempt {attempt + 1}/{max_retries}, URL {url_index + 1}/{len(urls_to_try)}, config {config_index + 1}/{len(connection_configs)})")
                        logger.info(f"MongoDB URL: {mongodb_url}")
                        logger.info(f"MongoDB Database: {settings.mongodb_db}")
                        logger.info(f"TLS Configuration: {config}")
                        
                        # Create client with current configuration
                        self.client = AsyncIOMotorClient(
                            mongodb_url,
                            **config
                        )
                        
                        # Test the connection
                        await self.client.admin.command('ping')
                        
                        self.db = self.client[settings.mongodb_db]
                        
                        # Create indexes with error handling
                        try:
                            await self.db.users.create_index([("google_id", ASCENDING)], unique=True)
                            await self.db.users.create_index([("email", ASCENDING)], unique=True)
                            await self.db.email_jobs.create_index([("user_id", ASCENDING)])
                            await self.db.email_jobs.create_index([("next_send", ASCENDING)])
                            await self.db.email_jobs.create_index([("status", ASCENDING)])
                            logger.info("Database indexes created successfully")
                        except Exception as index_error:
                            logger.warning(f"Failed to create some indexes: {index_error}")
                            # Continue even if index creation fails
                        
                        logger.info(f"Successfully connected to MongoDB using URL {url_index + 1} and configuration {config_index + 1}")
                        return
                        
                    except Exception as e:
                        logger.warning(f"URL {url_index + 1}, Configuration {config_index + 1} failed: {e}")
                        if self.client:
                            self.client.close()
                            self.client = None
                        continue
            
            # If all configurations failed, wait and retry
            logger.error(f"All connection configurations failed (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Failed to connect to MongoDB after all retries and configurations")
                raise Exception("All MongoDB connection attempts failed")

    async def close_mongo_connection(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")

    # User operations
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        user_dict = user.dict()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.users.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        return User(**user_dict)

    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        user_dict = await self.db.users.find_one({"google_id": google_id})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            return User(**user_dict)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_dict = await self.db.users.find_one({"email": email})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            return User(**user_dict)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by MongoDB _id."""
        from bson import ObjectId
        try:
            user_dict = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if user_dict:
                user_dict["id"] = str(user_dict["_id"])
                return User(**user_dict)
        except Exception as e:
            logger.error(f"Error getting user by id {user_id}: {e}")
        return None

    async def update_user_tokens(self, user_id: str, access_token: str, refresh_token: str, token_expiry: datetime):
        """Update user's OAuth tokens."""
        await self.db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_expiry": token_expiry,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    # Email job operations
    async def create_email_job(self, email_job: EmailJob) -> EmailJob:
        """Create a new email job."""
        job_dict = email_job.dict()
        job_dict["created_at"] = datetime.utcnow()
        job_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.email_jobs.insert_one(job_dict)
        job_dict["id"] = str(result.inserted_id)
        return EmailJob(**job_dict)

    async def get_user_email_jobs(self, user_id: str) -> List[EmailJob]:
        """Get all email jobs for a user."""
        cursor = self.db.email_jobs.find({"user_id": user_id, "status": {"$ne": EmailJobStatus.DELETED}})
        jobs = []
        async for job_dict in cursor:
            job_dict["id"] = str(job_dict["_id"])
            jobs.append(EmailJob(**job_dict))
        return jobs

    async def get_email_job(self, job_id: str, user_id: str) -> Optional[EmailJob]:
        """Get a specific email job."""
        from bson import ObjectId
        job_dict = await self.db.email_jobs.find_one({"_id": ObjectId(job_id), "user_id": user_id})
        if job_dict:
            job_dict["id"] = str(job_dict["_id"])
            return EmailJob(**job_dict)
        return None

    async def update_email_job(self, job_id: str, user_id: str, update_data: dict) -> Optional[EmailJob]:
        """Update an email job."""
        from bson import ObjectId
        update_data["updated_at"] = datetime.utcnow()
        result = await self.db.email_jobs.update_one(
            {"_id": ObjectId(job_id), "user_id": user_id},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_email_job(job_id, user_id)
        return None

    async def delete_email_job(self, job_id: str, user_id: str) -> bool:
        """Soft delete an email job."""
        from bson import ObjectId
        result = await self.db.email_jobs.update_one(
            {"_id": ObjectId(job_id), "user_id": user_id},
            {
                "$set": {
                    "status": EmailJobStatus.DELETED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    async def get_due_email_jobs(self) -> List[EmailJob]:
        """Get all email jobs that are due to be sent."""
        now = datetime.utcnow()
        cursor = self.db.email_jobs.find({
            "status": EmailJobStatus.ACTIVE,
            "$or": [
                {"next_send": {"$lte": now}},
                {"next_send": None}
            ]
        })
        jobs = []
        async for job_dict in cursor:
            job_dict["id"] = str(job_dict["_id"])
            jobs.append(EmailJob(**job_dict))
        return jobs

    async def update_job_sent_time(self, job_id: str, sent_time: datetime, next_send: datetime):
        """Update job's last sent time and next send time."""
        from bson import ObjectId
        await self.db.email_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "last_sent": sent_time,
                    "next_send": next_send,
                    "updated_at": datetime.utcnow()
                }
            }
        )


# Create database instance
db = Database() 