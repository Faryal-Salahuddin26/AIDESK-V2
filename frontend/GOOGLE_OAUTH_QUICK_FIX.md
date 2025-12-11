# QUICK FIX: Google OAuth redirect_uri_mismatch

## The Problem
Google is rejecting the redirect URI because it's not in your Google Cloud Console.

## The Solution (2 Minutes)

### Step 1: Open Google Cloud Console
**Direct Link**: https://console.cloud.google.com/apis/credentials

### Step 2: Find Your OAuth Client
1. Look for: **OAuth 2.0 Client IDs**
2. Find the one with Client ID starting with: `835198348471-...`
3. **Click on it** to edit

### Step 3: Add Redirect URI
1. Scroll down to **"Authorized redirect URIs"**
2. Click **"+ ADD URI"**
3. **Copy and paste this EXACT text**:
   ```
   http://localhost:3000/api/auth/callback/google
   ```
4. **IMPORTANT**: 
   - Use `http://` NOT `https://`
   - No trailing slash
   - Use `localhost` NOT `127.0.0.1`
   - Port must be `3000` (or `3001` if your server uses that)

### Step 4: Save
1. Click **"SAVE"** button at the bottom
2. Wait 1-2 minutes for Google to update

### Step 5: Test
1. Restart your dev server (Ctrl+C, then `npm run dev`)
2. Go to http://localhost:3000/login
3. Click "Sign in with Google"
4. It should work now!

## Still Not Working?

### Check What Redirect URI Is Actually Being Sent:

1. Open browser DevTools (Press F12)
2. Go to **Network** tab
3. Click "Sign in with Google" button
4. Look for a request to `accounts.google.com`
5. Click on it
6. In the **Headers** tab, find the **Request URL**
7. Look for `redirect_uri=` in the URL
8. Copy the value after `redirect_uri=`
9. Make sure THIS EXACT URI is in Google Cloud Console

### Common Mistakes:
- ❌ Using `https://localhost` instead of `http://localhost`
- ❌ Adding trailing slash: `/api/auth/callback/google/`
- ❌ Using wrong port (3001 instead of 3000)
- ❌ Not clicking SAVE in Google Cloud Console
- ❌ Not waiting for changes to propagate (wait 1-2 minutes)

## Need Help?
Check the server console - it will show the expected callback URL when NextAuth initializes.

