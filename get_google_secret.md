# 🔑 Get Your Google Client Secret

## Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com
2. Select your project: `383809440934`

## Step 2: Navigate to OAuth2 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Find your OAuth 2.0 Client ID: `383809440934-j3j60ub8fmmfgf1b34p65lp5pqvt0g8k.apps.googleusercontent.com`
3. Click on it to view details

## Step 3: Get the Client Secret
1. Click "Download JSON" or "Show Secret"
2. Copy the `client_secret` value
3. It looks like: `GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Step 4: Add to Railway
1. In Railway dashboard, add environment variable:
   ```
   GOOGLE_CLIENT_SECRET=GOCSPX-your_actual_secret_here
   ```

## Step 5: Update Redirect URI
1. In the same OAuth2 credentials page
2. Add your Railway domain to "Authorized redirect URIs":
   ```
   https://your-app-name.railway.app/auth/google/callback
   ```

## Step 6: Enable Gmail API
1. Go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Enable"

Your app will then be fully functional! 🚀 