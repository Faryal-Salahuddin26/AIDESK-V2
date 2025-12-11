# Google OAuth Setup Verification

## Current Configuration

Your Google OAuth credentials are configured in `.env.local`:
- `GOOGLE_CLIENT_ID`: your-client-id.apps.googleusercontent.com
- `GOOGLE_CLIENT_SECRET`: your-client-secret

## Required Google Cloud Console Settings

### 1. Authorized Redirect URIs

Make sure these redirect URIs are added in your Google Cloud Console:

**For Development:**
```
http://localhost:3000/api/auth/callback/google
```

**For Production (when deployed):**
```
https://yourdomain.com/api/auth/callback/google
```

### 2. How to Add Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Under **Authorized redirect URIs**, click **+ ADD URI**
6. Add: `http://localhost:3000/api/auth/callback/google`
7. Click **SAVE**

### 3. Verify OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Make sure the consent screen is configured
3. Add your email as a test user if the app is in testing mode

### 4. Enable Google+ API (if needed)

1. Go to **APIs & Services** > **Library**
2. Search for "Google+ API" or "Google Identity"
3. Make sure it's enabled

## Testing

After adding the redirect URI:
1. Restart your Next.js dev server
2. Go to `/login` page
3. Click the "Google" button
4. You should be redirected to Google's sign-in page
5. After signing in, you'll be redirected back to your app

## Common Issues

1. **"redirect_uri_mismatch" error**: The redirect URI in Google Console doesn't match exactly
2. **"access_denied" error**: User cancelled the OAuth flow or consent screen isn't configured
3. **"invalid_client" error**: Client ID or Secret is incorrect

## Next Steps

1. Verify the redirect URI is added in Google Cloud Console
2. Restart the dev server
3. Test the Google OAuth flow

