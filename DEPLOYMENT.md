# 🚀 Deployment Guide - Email Scheduler SaaS

## Deploy to Railway (Free & Easy)

### Step 1: Create Railway Account
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub account
3. Get $5 free credit (enough for small apps)

### Step 2: Connect Your Repository
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select your `JobReminder` repository

### Step 3: Add Environment Variables
In Railway dashboard, add these environment variables:

```env
# MongoDB (Already configured in code)
MONGODB_URL=mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/
MONGODB_DB=email_scheduler

# Google OAuth2 (You need to add your secret)
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret_here

# JWT (Already configured in code)
JWT_SECRET_KEY=your_super_secret_jwt_key_that_should_be_at_least_32_characters_long_for_security

# Production Settings
DEBUG=False
PORT=8000
```

### Step 4: Update Google OAuth2 Redirect URI
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to your OAuth2 app
3. Add your Railway domain to authorized redirect URIs:
   ```
   https://your-app-name.railway.app/auth/google/callback
   ```

### Step 5: Update Frontend API Base
1. Get your Railway domain (e.g., `https://your-app-name.railway.app`)
2. Update `frontend_example.html` line ~270:
   ```javascript
   const API_BASE = 'https://your-app-name.railway.app';
   ```

### Step 6: Deploy
1. Railway will auto-deploy when you push to GitHub
2. Or click "Deploy Now" in Railway dashboard
3. Wait for deployment to complete

### Step 7: Test Your Live App
1. Visit your Railway domain
2. Test Google OAuth2 login
3. Create email jobs
4. Test email sending (after enabling Gmail API)

## Alternative Free Platforms

### Render (Also Great)
- Free tier: 750 hours/month
- Auto-deploys from GitHub
- Built-in PostgreSQL

### Fly.io (Developer Friendly)
- Free tier: 3 shared-cpu VMs
- Global deployment
- Docker support

## Important Notes

1. **Google Client Secret**: You MUST add your actual Google client secret
2. **Gmail API**: Still need to enable in Google Cloud Console
3. **Custom Domain**: Railway provides free SSL certificates
4. **Monitoring**: Check Railway logs for any issues

## Troubleshooting

- **Build Errors**: Check Railway logs
- **Database Issues**: Verify MongoDB Atlas connection
- **OAuth Errors**: Check redirect URI configuration
- **Email Not Sending**: Enable Gmail API in Google Cloud Console

Your app will be live at: `https://your-app-name.railway.app` 🎉 