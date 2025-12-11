import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import AppleProvider from "next-auth/providers/apple"
import CredentialsProvider from "next-auth/providers/credentials"

// Ensure we have a secret
const secret = process.env.NEXTAUTH_SECRET || process.env.JWT_SECRET
if (!secret) {
  console.warn("⚠️ Warning: NEXTAUTH_SECRET or JWT_SECRET not set. Authentication may not work properly.")
}

// Get the base URL for callbacks
const getBaseUrl = () => {
  if (process.env.NEXTAUTH_URL) {
    return process.env.NEXTAUTH_URL;
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return "http://localhost:3000";
};

const baseUrl = getBaseUrl();

// Log configuration for debugging
if (process.env.NODE_ENV === "development") {
  console.log("🔍 NextAuth Configuration:");
  console.log("  Base URL:", baseUrl);
  console.log("  NEXTAUTH_URL env:", process.env.NEXTAUTH_URL || "NOT SET");
  console.log("  Expected callback URL:", `${baseUrl}/api/auth/callback/google`);
  console.log("  Google Client ID:", process.env.GOOGLE_CLIENT_ID ? `${process.env.GOOGLE_CLIENT_ID.substring(0, 20)}...` : "NOT SET");
  console.log("  Google Client Secret:", process.env.GOOGLE_CLIENT_SECRET ? "SET" : "NOT SET");
  console.log("");
  console.log("⚠️  IMPORTANT: Add this exact URL to Google Cloud Console:");
  console.log(`   ${baseUrl}/api/auth/callback/google`);
  console.log("");
}

export const authOptions: NextAuthOptions = {
  debug: process.env.NODE_ENV === "development",
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
        },
      },
    }),
    // Apple Provider - requires Apple Developer account
    // Configure when you have Apple credentials
    ...(process.env.APPLE_ID && process.env.APPLE_TEAM_ID && process.env.APPLE_KEY_ID && process.env.APPLE_PRIVATE_KEY
      ? [
          AppleProvider({
            clientId: process.env.APPLE_ID,
            clientSecret: {
              appleId: process.env.APPLE_ID,
              teamId: process.env.APPLE_TEAM_ID,
              keyId: process.env.APPLE_KEY_ID,
              privateKey: process.env.APPLE_PRIVATE_KEY.replace(/\\n/g, "\n"),
            },
          }),
        ]
      : []),
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
          const response = await fetch(`${apiUrl}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          })

          if (response.ok) {
            const user = await response.json()
            return {
              id: user.id || credentials.email,
              email: user.email || credentials.email,
              name: user.name || user.email?.split("@")[0] || credentials.email,
            }
          } else {
            const errorData = await response.json().catch(() => ({ detail: "Login failed" }))
            console.error("Login error:", errorData.detail || "Invalid credentials")
            return null
          }
        } catch (error) {
          console.error("Auth error:", error)
          return null
        }
      }
    })
  ],
  pages: {
    signIn: "/login",
    signOut: "/",
    error: "/auth/error",
  },
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id
      }
      if (account) {
        token.accessToken = account.access_token
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
      }
      return session
    },
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  secret: secret || "your-secret-key-change-in-production",
  trustHost: true, // Required for NextAuth v5
  // Explicitly set the base URL for callbacks
  basePath: "/api/auth",
  // Ensure we use the correct base URL
  url: baseUrl,
}

// NextAuth v5 beta - export handler directly
const { handlers } = NextAuth(authOptions)

export const { GET, POST } = handlers

// Export authOptions for use in other files if needed
export { authOptions }

