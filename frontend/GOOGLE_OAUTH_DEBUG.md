# Google OAuth redirect_uri_mismatch - Debug Guide

## Current Configuration

- **NEXTAUTH_URL**: `http://localhost:3000`
- **Expected Redirect URI**: `http://localhost:3000/api/auth/callback/google`
- **Google Client ID**: `835198348471-irvthbimqivduhqqruno5ekvf344gp1m.apps.googleusercontent.com`

## Step-by-Step Fix

### 1. Check What Port Your Server Is Running On

Open your terminal where `npm run dev` is running and check:
- If it says `Local: http://localhost:3000` → Use port 3000
- If it says `Local: http://localhost:3001` → Use port 3001

### 2. Add Redirect URI in Google Cloud Console

**CRITICAL**: The redirect URI must match EXACTLY what NextAuth sends.

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID (835198348471-...)
3. Under **"Authorized redirect URIs"**, add BOTH:

   **For port 3000:**
   ```
   http://localhost:3000/api/auth/callback/google
   ```

   **For port 3001 (if your server uses this):**
   ```
   http://localhost:3001/api/auth/callback/google
   ```

4. Click **SAVE**
5. Wait 2-3 minutes for changes to propagate

### 3. Verify Redirect URI Format

The redirect URI must be:
- ✅ `http://localhost:3000/api/auth/callback/google` (correct)
- ❌ `https://localhost:3000/api/auth/callback/google` (wrong - don't use https)
- ❌ `http://localhost:3000/api/auth/callback/google/` (wrong - no trailing slash)
- ❌ `http://127.0.0.1:3000/api/auth/callback/google` (wrong - use localhost, not 127.0.0.1)

### 4. Check Browser Console

When you click "Sign in with Google", check the browser console (F12) and look for:
- The actual redirect URI being used
- Any error messages

### 5. Test the OAuth Flow

1. Clear browser cache (Ctrl+Shift+Delete)
2. Restart your dev server
3. Go to `/login`
4. Click "Sign in with Google"
5. Check if it redirects properly

## Still Not Working?

### Option A: Check Actual Redirect URI Being Sent

1. Open browser DevTools (F12)
2. Go to Network tab
3. Click "Sign in with Google"
4. Look for the request to `accounts.google.com`
5. Check the `redirect_uri` parameter in the URL
6. Make sure this EXACT URI is in Google Cloud Console

### Option B: Add Multiple Redirect URIs

Add all these to Google Cloud Console (just to be safe):

```
http://localhost:3000/api/auth/callback/google
http://localhost:3001/api/auth/callback/google
http://127.0.0.1:3000/api/auth/callback/google
http://127.0.0.1:3001/api/auth/callback/google
```

### Option C: Verify OAuth Consent Screen

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Make sure OAuth consent screen is configured
3. Add your email as a test user if app is in testing mode

## Common Issues

1. **Changes not saved**: Make sure you clicked SAVE in Google Cloud Console
2. **Wrong port**: Check which port your server is actually using
3. **Cache issues**: Clear browser cache and restart server
4. **Typo in URI**: Copy-paste the URI exactly, no spaces or extra characters

