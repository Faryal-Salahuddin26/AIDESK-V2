# How to Verify and Fix Google OAuth Redirect URI

## Step 1: Check What Redirect URI NextAuth Is Actually Sending

1. **Open your browser DevTools** (Press F12)
2. Go to the **Network** tab
3. Clear the network log
4. Click "Sign in with Google" button
5. Look for a request to `accounts.google.com` or `oauth2.googleapis.com`
6. Click on that request
7. Go to the **Headers** tab
8. Look at the **Request URL** - it will look something like:
   ```
   https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...
   ```
9. **Copy the exact value** after `redirect_uri=` (it will be URL-encoded)

## Step 2: Decode the Redirect URI

The redirect URI will be URL-encoded. It should decode to something like:
```
http://localhost:3000/api/auth/callback/google
```

## Step 3: Add to Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID (the one starting with `835198348471-...`)
3. Scroll to **"Authorized redirect URIs"**
4. Click **"+ ADD URI"**
5. **Paste the EXACT decoded redirect URI** from Step 2
6. Click **SAVE**
7. **Wait 1-2 minutes** for Google to update

## Step 4: Common Issues

### Issue: Redirect URI doesn't match
- Make sure there are **no trailing slashes**
- Make sure you're using `http://` not `https://` for localhost
- Make sure you're using `localhost` not `127.0.0.1`
- Make sure the port matches (3000 or 3001)

### Issue: Still getting error after adding
- Clear your browser cache (Ctrl+Shift+Delete)
- Restart your dev server
- Wait 2-3 minutes for Google's changes to propagate
- Try in an incognito/private window

### Issue: Multiple redirect URIs
If your app might run on different ports, add ALL possible redirect URIs:
```
http://localhost:3000/api/auth/callback/google
http://localhost:3001/api/auth/callback/google
http://127.0.0.1:3000/api/auth/callback/google
```

## Step 5: Verify It's Working

After adding the redirect URI:
1. Restart your dev server
2. Go to `/login`
3. Click "Sign in with Google"
4. You should be redirected to Google's sign-in page
5. After signing in, you should be redirected back to your app

If you still get an error, check the browser console and network tab to see what redirect URI is being sent.

