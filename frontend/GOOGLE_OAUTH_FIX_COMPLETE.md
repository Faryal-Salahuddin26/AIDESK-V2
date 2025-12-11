# Complete Google OAuth Fix Guide

## Step 1: Check Your Configuration

I've created a debug endpoint. Open this URL in your browser:
```
http://localhost:3000/api/auth/debug
```

This will show you the **exact redirect URI** that NextAuth is using.

## Step 2: Add Redirect URI to Google Cloud Console

1. **Open Google Cloud Console**: https://console.cloud.google.com/apis/credentials

2. **Find Your OAuth Client**:
   - Look for "OAuth 2.0 Client IDs"
   - Find the one with Client ID: `835198348471-irvthbimqivduhqqruno5ekvf344gp1m`
   - **Click on it** to edit

3. **Add Redirect URI**:
   - Scroll down to **"Authorized redirect URIs"**
   - Click **"+ ADD URI"**
   - **Copy and paste this EXACT URL** (from the debug endpoint):
     ```
     http://localhost:3000/api/auth/callback/google
     ```
   - **IMPORTANT**: 
     - Use `http://` NOT `https://`
     - No trailing slash
     - Use `localhost` NOT `127.0.0.1`
     - Port must be `3000` (or check what port your server uses)

4. **Save**:
   - Click **"SAVE"** button at the bottom
   - **Wait 1-2 minutes** for Google to update

## Step 3: Verify It's Added Correctly

After saving, verify:
1. The redirect URI appears in the list
2. There are no extra spaces or characters
3. It matches exactly: `http://localhost:3000/api/auth/callback/google`

## Step 4: Test

1. **Restart your dev server** (Ctrl+C, then `npm run dev`)
2. **Clear browser cache** (Ctrl+Shift+Delete)
3. Go to: `http://localhost:3000/login`
4. Click **"Sign in with Google"**
5. You should be redirected to Google's sign-in page
6. After signing in, you should be redirected back to your app

## Step 5: If Still Not Working

### Check Server Console

When you start your dev server, look for this output:
```
🔍 NextAuth Configuration:
  Expected callback URL: http://localhost:3000/api/auth/callback/google
```

Make sure this **exact URL** is in Google Cloud Console.

### Check Browser Network Tab

1. Open DevTools (F12)
2. Go to **Network** tab
3. Click "Sign in with Google"
4. Find request to `accounts.google.com`
5. Check the `redirect_uri` parameter in the URL
6. Make sure this **exact URI** is in Google Cloud Console

### Common Mistakes

- ❌ Using `https://localhost` instead of `http://localhost`
- ❌ Adding trailing slash: `/api/auth/callback/google/`
- ❌ Using wrong port (3001 instead of 3000)
- ❌ Using `127.0.0.1` instead of `localhost`
- ❌ Not clicking SAVE in Google Cloud Console
- ❌ Not waiting for changes to propagate (wait 1-2 minutes)

### Still Having Issues?

1. Check the debug endpoint: `http://localhost:3000/api/auth/debug`
2. Copy the `callbackUrl` from the response
3. Make sure this **exact URL** is in Google Cloud Console
4. Try in an incognito/private window
5. Clear all browser cookies for localhost

## What I Fixed

1. ✅ Added explicit `url` configuration to NextAuth
2. ✅ Improved base URL detection
3. ✅ Added comprehensive logging
4. ✅ Created debug endpoint to show exact redirect URI
5. ✅ Updated OAuth sign-in handlers

The redirect URI **MUST** match exactly what NextAuth sends. Use the debug endpoint to see what it is!

