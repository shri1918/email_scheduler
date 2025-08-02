# Email Scheduler - SaaS Recurring Email Service

A FastAPI-based SaaS application that enables users to schedule recurring emails using their Gmail accounts with OAuth2 authentication. The service supports multiple users, secure token management, and background email scheduling.

## Features

- 🔐 **Google OAuth2 Authentication** - Secure authentication using Google accounts
- 📧 **Gmail API Integration** - Send emails through Gmail API (not SMTP)
- ⏰ **Recurring Email Scheduling** - Schedule emails to be sent every N days
- 📎 **File Attachments** - Support for email attachments
- 🔄 **Token Refresh** - Automatic refresh of expired access tokens
- 👥 **Multi-tenancy** - Each user manages their own email schedules
- 🎯 **Background Processing** - APScheduler for reliable email delivery
- 📊 **MongoDB Storage** - Scalable data storage with MongoDB
- 🛡️ **Secure Token Storage** - Encrypted storage of OAuth tokens

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   MongoDB       │
│   (React/Vue)   │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   APScheduler   │
                       │   Background    │
                       │   Email Jobs    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Gmail API     │
                       │   OAuth2        │
                       └─────────────────┘
```

## Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- Google Cloud Project with Gmail API enabled
- Google OAuth2 credentials

## Quick Start

### Local Development
See [SETUP.md](SETUP.md) for detailed local development setup.

### Railway Deployment
See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for Railway deployment instructions.

### Deployment Verification
Run the deployment check script to verify your configuration:
```bash
python railway_check.py
```

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd JobReminder

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
   - Note down the Client ID and Client Secret

### 3. Environment Configuration

Create a `.env` file based on `env.example`:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=email_scheduler

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here_make_it_long_and_random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_NAME=Email Scheduler
DEBUG=True
HOST=0.0.0.0
PORT=8000

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=uploads
```

### 4. Start MongoDB

```bash
# Install MongoDB (if not already installed)
# On macOS with Homebrew:
brew install mongodb-community

# Start MongoDB
mongod

# Or use MongoDB Atlas (cloud service)
```

### 5. Run the Application

```bash
# Start the FastAPI server
python main.py

# Or using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### Authentication Endpoints

#### GET `/auth/google`
Initiate Google OAuth2 authentication.

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

#### GET `/auth/google/callback`
Handle OAuth2 callback (redirects to frontend with JWT token).

#### GET `/auth/me`
Get current user information.

**Headers:** `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "google_id": "google_user_id",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST `/auth/test-connection`
Test Gmail connection.

**Response:**
```json
{
  "valid": true
}
```

### Email Job Endpoints

#### POST `/jobs`
Create a new email job.

**Request Body:**
```json
{
  "recipient": "recipient@example.com",
  "subject": "Test Email",
  "body": "This is a test email body",
  "attachments": ["/path/to/file.pdf"],
  "every_n_days": 7
}
```

#### GET `/jobs`
Get all email jobs for the current user.

#### GET `/jobs/{job_id}`
Get a specific email job.

#### PUT `/jobs/{job_id}`
Update an email job.

**Request Body:**
```json
{
  "recipient": "newrecipient@example.com",
  "subject": "Updated Subject",
  "body": "Updated body",
  "every_n_days": 14,
  "status": "paused"
}
```

#### DELETE `/jobs/{job_id}`
Delete an email job.

#### POST `/jobs/{job_id}/pause`
Pause an email job.

#### POST `/jobs/{job_id}/resume`
Resume a paused email job.

#### POST `/jobs/{job_id}/send-now`
Send an email immediately.

### File Upload Endpoints

#### POST `/upload`
Upload a file for email attachments.

**Headers:** `Authorization: Bearer <jwt_token>`

**Form Data:** `file: <file>`

**Response:**
```json
{
  "filename": "document.pdf",
  "file_path": "/uploads/user_id/document.pdf",
  "size": 1024
}
```

### Health Check

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "scheduler_running": true
}
```

## Usage Examples

### 1. User Authentication Flow

```javascript
// Frontend JavaScript example
async function authenticate() {
  // Redirect to Google OAuth
  window.location.href = 'http://localhost:8000/auth/google';
}

// Handle callback
function handleAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  
  if (token) {
    localStorage.setItem('auth_token', token);
    // Redirect to dashboard
  }
}
```

### 2. Create Email Job

```javascript
async function createEmailJob() {
  const response = await fetch('http://localhost:8000/jobs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
    },
    body: JSON.stringify({
      recipient: 'friend@example.com',
      subject: 'Weekly Update',
      body: 'Here is your weekly update...',
      every_n_days: 7
    })
  });
  
  const job = await response.json();
  console.log('Email job created:', job);
}
```

### 3. Upload File

```javascript
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
    },
    body: formData
  });
  
  const result = await response.json();
  console.log('File uploaded:', result);
}
```

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "name": "John Doe",
  "google_id": "google_user_id",
  "access_token": "encrypted_access_token",
  "refresh_token": "encrypted_refresh_token",
  "token_expiry": "2024-01-01T01:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Email Jobs Collection
```json
{
  "_id": "ObjectId",
  "user_id": "user_object_id",
  "recipient": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body content",
  "attachments": ["/path/to/file1.pdf", "/path/to/file2.jpg"],
  "every_n_days": 7,
  "last_sent": "2024-01-01T00:00:00Z",
  "next_send": "2024-01-08T00:00:00Z",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Security Features

- **OAuth2 Authentication**: Secure Google authentication
- **JWT Tokens**: Stateless authentication
- **Token Refresh**: Automatic refresh of expired tokens
- **Encrypted Storage**: Secure storage of sensitive tokens
- **Multi-tenancy**: User isolation
- **File Upload Security**: Size limits and user-specific directories

## Error Handling

The application handles various error scenarios:

- **Token Expiration**: Automatic refresh with fallback to re-authentication
- **Gmail API Errors**: Graceful handling of API failures
- **Database Errors**: Proper error responses
- **File Upload Errors**: Size and format validation
- **Network Errors**: Retry mechanisms for email sending

## Monitoring and Logging

- **Structured Logging**: Comprehensive logging throughout the application
- **Health Checks**: Application health monitoring
- **Scheduler Status**: Background job monitoring
- **Error Tracking**: Detailed error logging for debugging

## Deployment

### Railway Deployment (Recommended)

The application is optimized for Railway deployment with:
- Environment variable configuration
- Database connection retry logic
- Health check endpoints
- Graceful error handling

See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed instructions.

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```env
MONGODB_URL=mongodb://your-mongodb-url
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
GOOGLE_REDIRECT_URI=https://your-domain.com/auth/google/callback
JWT_SECRET_KEY=your-production-secret-key
DEBUG=False
```

## Recent Updates

### Railway Deployment Fixes (Latest)

- ✅ Fixed MongoDB connection issues on Railway
- ✅ Added environment variable support for all configuration
- ✅ Implemented database connection retry logic
- ✅ Enhanced error handling and logging
- ✅ Added health check endpoint with database status
- ✅ Created Railway deployment verification script
- ✅ Updated Google OAuth redirect URI handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on GitHub. 