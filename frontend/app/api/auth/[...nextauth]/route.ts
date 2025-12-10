import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import AppleProvider from "next-auth/providers/apple"
import CredentialsProvider from "next-auth/providers/credentials"

// Ensure we have a secret
const secret = process.env.NEXTAUTH_SECRET || process.env.JWT_SECRET
if (!secret) {
  console.warn("⚠️ Warning: NEXTAUTH_SECRET or JWT_SECRET not set. Authentication may not work properly.")
}

export const authOptions: NextAuthOptions = {
  debug: process.env.NODE_ENV === "development",
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
      allowDangerousEmailAccountLinking: true,
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

        // TODO: Replace with actual API call to your backend
        // For now, this is a placeholder
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
              email: credentials.email,
              name: user.name || credentials.email,
            }
          }
        } catch (error) {
          console.error("Auth error:", error)
        }

        return null
      }
    })
  ],
  pages: {
    signIn: "/login",
    signOut: "/",
    error: "/login",
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
}

// Initialize NextAuth handler
let handler: ReturnType<typeof NextAuth>

try {
  handler = NextAuth(authOptions)
} catch (error) {
  console.error("Failed to initialize NextAuth:", error)
  // Create a fallback handler that returns proper error JSON
  handler = NextAuth({
    ...authOptions,
    providers: [], // Empty providers as fallback
  })
}

export { handler as GET, handler as POST }

// Export authOptions for use in other files if needed
export { authOptions }

