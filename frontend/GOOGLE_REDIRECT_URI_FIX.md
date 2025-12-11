# Fix Google OAuth redirect_uri_mismatch Error

## Error: redirect_uri_mismatch

This error occurs when the redirect URI in your Google Cloud Console doesn't match what NextAuth is sending.

## Solution: Add Redirect URI to Google Cloud Console

### Step-by-Step Instructions:

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Make sure you're in the correct project

2. **Find Your OAuth 2.0 Client**
   - Look for your OAuth 2.0 Client ID
   - Click on it to edit

3. **Add Authorized Redirect URI**
   - Scroll down to **"Authorized redirect URIs"** section
   - Click **"+ ADD URI"** button
   - Add this EXACT URI (copy and paste):
     ```
     http://localhost:3000/api/auth/callback/google
     ```
   - ⚠️ **IMPORTANT**: Make sure there are no trailing spaces or extra characters
   - The URI must match EXACTLY

4. **Save Changes**
   - Click **"SAVE"** at the bottom of the page
   - Wait a few seconds for changes to propagate

5. **Test Again**
   - Restart your Next.js dev server (if running)
   - Go to `/login` page
   - Click "Sign in with Google"
   - It should now work!

## For Production Deployment

When you deploy to production (e.g., Vercel), you'll need to add another redirect URI:

```
https://yourdomain.com/api/auth/callback/google
```

Replace `yourdomain.com` with your actual domain.

## Common Mistakes to Avoid

1. ❌ Using `https://` instead of `http://` for localhost
2. ❌ Adding trailing slashes: `http://localhost:3000/api/auth/callback/google/`
3. ❌ Using wrong port: Make sure it's port `3000` (or `3001` if 3000 is busy)
4. ❌ Typos in the URI path
5. ❌ Not saving the changes in Google Cloud Console

## Verify Your Setup

Your `.env.local` should have:
```
NEXTAUTH_URL=http://localhost:3000
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

## Still Not Working?

1. Check the browser console for the exact redirect URI being used
2. Verify the redirect URI in Google Cloud Console matches exactly
3. Make sure you saved the changes in Google Cloud Console
4. Wait 1-2 minutes for Google's changes to propagate
5. Clear browser cache and try again

