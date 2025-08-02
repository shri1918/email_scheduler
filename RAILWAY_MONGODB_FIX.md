# Railway MongoDB Connection Fix Guide

## Problem
Railway deployments often have SSL/TLS handshake issues with MongoDB Atlas due to:
- Network restrictions
- SSL certificate validation
- TLS version compatibility
- Railway's container environment

## Solution
This guide provides multiple strategies to resolve MongoDB connection issues on Railway.

## Step 1: Update Environment Variables

Set these environment variables in your Railway dashboard:

### Option A: Use Connection String with Query Parameters (Recommended)
```bash
MONGODB_URL=mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/email_scheduler?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true
MONGODB_DB=email_scheduler
```

### Option B: Use Alternative Connection String
```bash
MONGODB_URL=mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/email_scheduler?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true&tlsAllowInvalidHostnames=true
MONGODB_DB=email_scheduler
```

### Option C: Use Railway MongoDB Plugin (Best Practice)
1. Add MongoDB plugin to your Railway project
2. Railway will automatically set `MONGODB_URL`
3. Set only: `MONGODB_DB=email_scheduler`

## Step 2: MongoDB Atlas Configuration

### Network Access
1. Go to MongoDB Atlas → Network Access
2. Add IP Address: `0.0.0.0/0` (Allow access from anywhere)
3. Or add Railway's IP ranges if known

### Database Access
1. Go to MongoDB Atlas → Database Access
2. Ensure your user has proper permissions
3. Reset password if needed

### Cluster Settings
1. Go to MongoDB Atlas → Clusters
2. Click on your cluster
3. Ensure it's active and running

## Step 3: Alternative Solutions

### Solution 1: Use Railway MongoDB Plugin
```bash
# In Railway dashboard, add MongoDB plugin
# This automatically handles connection issues
```

### Solution 2: Use Different MongoDB Provider
Consider using:
- Railway's built-in MongoDB
- PlanetScale
- Supabase
- Other Railway-compatible databases

### Solution 3: Use Connection Pooling
```bash
MONGODB_URL=mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/email_scheduler?retryWrites=true&w=majority&maxPoolSize=10&minPoolSize=1
```

## Step 4: Testing Connection

### Local Test
```bash
python test_mongodb_connection.py
```

### Railway Test
Check the logs for successful connection:
```
INFO:database:Successfully connected to MongoDB using URL 1 and strategy 1
```

## Step 5: Troubleshooting

### If Still Failing:
1. **Check MongoDB Atlas Status**: Ensure cluster is active
2. **Verify Credentials**: Check username/password
3. **Network Access**: Ensure 0.0.0.0/0 is allowed
4. **Try Different Region**: Some regions may have better connectivity
5. **Use Railway MongoDB**: Switch to Railway's MongoDB plugin

### Common Error Messages:
- `SSL handshake failed`: Use `tlsAllowInvalidCertificates=true`
- `connection closed`: Check network access settings
- `authentication failed`: Verify username/password
- `timeout`: Increase timeout values

## Step 6: Final Configuration

### Recommended Environment Variables:
```bash
# MongoDB Configuration
MONGODB_URL=mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/email_scheduler?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true
MONGODB_DB=email_scheduler

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=383809440934-j3j60ub8fmmfgf1b34p65lp5pqvt0g8k.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-railway-app.railway.app/auth/google/callback

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_that_should_be_at_least_32_characters_long_for_security

# Application Configuration
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

## Success Indicators

When working correctly, you should see:
```
INFO:database:Successfully connected to MongoDB using URL 1 and strategy 1
INFO:database:Database indexes created successfully
INFO:api:Application started successfully
```

## Support

If issues persist:
1. Check Railway logs for detailed error messages
2. Test connection locally first
3. Consider switching to Railway MongoDB plugin
4. Contact Railway support for network issues 