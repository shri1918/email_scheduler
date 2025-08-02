# Railway Deployment Guide

## Prerequisites

1. A Railway account
2. A MongoDB database (MongoDB Atlas or Railway MongoDB plugin)
3. Google OAuth2 credentials

## Deployment Steps

### 1. Deploy to Railway

1. Connect your GitHub repository to Railway
2. Create a new service from your repository
3. Railway will automatically detect the Python project and deploy it

### 2. Set Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add the following environment variables:

#### Required Variables:

```bash
# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=email_scheduler

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-railway-app.railway.app/auth/google/callback

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_that_should_be_at_least_32_characters_long_for_security

# Application Configuration
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

#### Optional Variables:

```bash
# Application Configuration
APP_NAME=Email Scheduler
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_ALGORITHM=HS256

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
```

### 3. MongoDB Setup

#### Option A: MongoDB Atlas (Recommended)
1. Create a MongoDB Atlas cluster
2. Get your connection string
3. Set `MONGODB_URL` to your Atlas connection string
4. Set `MONGODB_DB` to your desired database name

#### Option B: Railway MongoDB Plugin
1. Add MongoDB plugin to your Railway project
2. Railway will automatically set `MONGODB_URL` environment variable
3. Set `MONGODB_DB` to your desired database name

### 4. Google OAuth2 Setup

1. Go to Google Cloud Console
2. Create or select a project
3. Enable Gmail API
4. Create OAuth2 credentials
5. Add your Railway domain to authorized redirect URIs:
   - `https://your-railway-app.railway.app/auth/google/callback`
6. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

### 5. Update Google OAuth Redirect URI

Make sure to update your Google OAuth2 redirect URI to use your Railway domain instead of localhost.

### 6. Deploy and Test

1. Railway will automatically redeploy when you push changes
2. Check the deployment logs for any errors
3. Test the health endpoint: `https://your-railway-app.railway.app/health`
4. Test the main application: `https://your-railway-app.railway.app/`

## Troubleshooting

### Database Connection Issues

If you see MongoDB connection errors:

1. Check that `MONGODB_URL` is correctly set
2. Verify your MongoDB credentials
3. Ensure your MongoDB cluster is accessible from Railway
4. Check the health endpoint for detailed connection status

### OAuth Issues

If Google OAuth is not working:

1. Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
2. Check that your Railway domain is in the authorized redirect URIs
3. Ensure Gmail API is enabled in Google Cloud Console

### Common Environment Variable Issues

- Make sure all required variables are set
- Check for typos in variable names
- Ensure values don't have extra spaces
- Use the correct format for URLs and connection strings

## Monitoring

- Use Railway's built-in logging to monitor your application
- Check the `/health` endpoint for application status
- Monitor database connections and performance
- Set up alerts for application errors

## Security Notes

- Never commit sensitive environment variables to your repository
- Use strong, unique JWT secret keys
- Regularly rotate your OAuth credentials
- Monitor your application logs for security issues 