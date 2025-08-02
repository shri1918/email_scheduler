# Quick Setup Guide

## 🚀 Getting Started

This guide will help you get the Email Scheduler up and running quickly.

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- Google Cloud Project with Gmail API enabled

### 1. Environment Setup

```bash
# Clone the repository (if not already done)
cd JobReminder

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup test
python3 test_setup.py
```

### 2. Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
   - Note down the Client ID and Client Secret

### 3. Configuration

Edit the `.env` file with your credentials:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=email_scheduler

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
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

### 6. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Frontend Example**: Open `frontend_example.html` in your browser
- **Health Check**: http://localhost:8000/health

## 🔧 Testing the Setup

Run the test script to verify everything is working:

```bash
python3 test_setup.py
```

You should see:
```
Test Results: 4/4 tests passed
All tests passed! Your setup is ready.
```

## 📧 Using the Application

### 1. Authentication

1. Visit http://localhost:8000/auth/google
2. Complete Google OAuth2 authentication
3. You'll be redirected back with a JWT token

### 2. Create Email Jobs

Use the API or the frontend example to:
- Create recurring email jobs
- Set recipients, subjects, and message bodies
- Configure send intervals (every N days)
- Upload attachments

### 3. Manage Jobs

- View all your email jobs
- Pause/resume jobs
- Send emails immediately
- Delete jobs

## 🛠️ API Endpoints

### Authentication
- `GET /auth/google` - Initiate Google OAuth2
- `GET /auth/me` - Get current user info
- `POST /auth/test-connection` - Test Gmail connection

### Email Jobs
- `POST /jobs` - Create email job
- `GET /jobs` - List all jobs
- `GET /jobs/{id}` - Get specific job
- `PUT /jobs/{id}` - Update job
- `DELETE /jobs/{id}` - Delete job
- `POST /jobs/{id}/pause` - Pause job
- `POST /jobs/{id}/resume` - Resume job
- `POST /jobs/{id}/send-now` - Send email now

### File Upload
- `POST /upload` - Upload attachment

## 🔍 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in `.env`

2. **Google OAuth2 Error**
   - Verify Client ID and Secret in `.env`
   - Check redirect URI matches Google Console

3. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

4. **Permission Errors**
   - Check file permissions for uploads directory
   - Ensure proper MongoDB access

### Logs

Check the console output for detailed error messages and logs.

## 🚀 Production Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Use a production MongoDB instance
3. Configure proper CORS settings
4. Use HTTPS for OAuth2 redirect URIs
5. Set strong JWT secret key
6. Configure proper file upload limits

## 📚 Documentation

- **Full README**: See `README.md` for comprehensive documentation
- **API Docs**: Visit http://localhost:8000/docs when running
- **Code Comments**: Check individual Python files for detailed comments

## 🆘 Support

If you encounter issues:

1. Run `python3 test_setup.py` to diagnose problems
2. Check the console logs for error messages
3. Verify all configuration in `.env`
4. Ensure all dependencies are installed correctly 