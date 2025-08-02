# Railway MongoDB Plugin Setup Guide

## Why Use Railway MongoDB Plugin?

The SSL/TLS handshake errors you're experiencing are common when connecting external MongoDB Atlas to Railway. The **Railway MongoDB Plugin** is the recommended solution because:

1. **No SSL/TLS Issues**: Railway handles all connection problems internally
2. **Automatic Configuration**: Railway sets up environment variables automatically
3. **Better Performance**: Direct connection within Railway's network
4. **Reliability**: No external network dependencies

## Step-by-Step Setup

### Step 1: Add MongoDB Plugin to Railway

1. Go to your Railway project dashboard
2. Click on your service (email_scheduler)
3. Go to the "Variables" tab
4. Click "New Variable" → "Reference"
5. Select "MongoDB" from the dropdown
6. Railway will automatically add the MongoDB plugin

### Step 2: Update Environment Variables

After adding the MongoDB plugin, Railway will automatically set:
- `MONGODB_URL` (automatically set by Railway)
- `MONGODB_DB` (you need to set this)

**Set this environment variable:**
```bash
MONGODB_DB=email_scheduler
```

### Step 3: Remove Old MongoDB URL

**Remove or comment out:**
```bash
# MONGODB_URL=mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/...
```

### Step 4: Redeploy

1. Railway will automatically redeploy when you add the plugin
2. Check the logs for successful connection
3. Test the health endpoint: `https://your-app.railway.app/health`

## Expected Results

### Successful Connection Log:
```
INFO:database:Successfully connected to MongoDB using URL 1 and strategy 1
INFO:database:Database indexes created successfully
INFO:api:Application started successfully
```

### Health Check Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "scheduler_running": true
}
```

## Alternative: Keep MongoDB Atlas

If you prefer to keep using MongoDB Atlas, try this connection string:

```bash
MONGODB_URL=mongodb+srv://shri66688:4mrOf12CkYQWUuAf@fastapicloud.g5qhi.mongodb.net/email_scheduler?retryWrites=true&w=majority&ssl=false
```

**Note**: This disables SSL entirely, which may not be secure for production.

## Troubleshooting

### If Railway MongoDB Plugin Doesn't Work:

1. **Check Plugin Status**: Ensure MongoDB plugin is active
2. **Verify Environment Variables**: Check that `MONGODB_URL` is set by Railway
3. **Check Logs**: Look for connection errors in Railway logs
4. **Restart Service**: Sometimes a restart helps

### If You Want to Keep MongoDB Atlas:

1. **Update Network Access**: Allow `0.0.0.0/0` in MongoDB Atlas
2. **Check Cluster Status**: Ensure cluster is active
3. **Verify Credentials**: Double-check username/password
4. **Try Different Region**: Some regions have better connectivity

## Recommended Approach

**Use Railway MongoDB Plugin** - It's the most reliable solution for Railway deployments and eliminates all SSL/TLS issues.

## Migration from MongoDB Atlas

If you have existing data in MongoDB Atlas:

1. **Export Data**: Use MongoDB Compass or `mongoexport`
2. **Import to Railway MongoDB**: Use `mongoimport` or MongoDB Compass
3. **Update Connection**: Switch to Railway MongoDB plugin
4. **Test Application**: Verify all functionality works

## Cost Comparison

- **MongoDB Atlas**: Free tier available, but may have connection issues
- **Railway MongoDB**: Included in Railway pricing, more reliable

## Final Recommendation

**Switch to Railway MongoDB Plugin** for the most reliable and hassle-free experience. 