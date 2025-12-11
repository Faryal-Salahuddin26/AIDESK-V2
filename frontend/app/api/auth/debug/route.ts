import { NextResponse } from "next/server";

export async function GET() {
  const baseUrl = process.env.NEXTAUTH_URL || "http://localhost:3000";
  const callbackUrl = `${baseUrl}/api/auth/callback/google`;
  
  return NextResponse.json({
    baseUrl,
    callbackUrl,
    googleClientId: process.env.GOOGLE_CLIENT_ID ? `${process.env.GOOGLE_CLIENT_ID.substring(0, 20)}...` : "NOT SET",
    hasGoogleSecret: !!process.env.GOOGLE_CLIENT_SECRET,
    nextAuthUrl: process.env.NEXTAUTH_URL,
    nodeEnv: process.env.NODE_ENV,
    instructions: {
      step1: "Copy the callbackUrl above",
      step2: "Go to https://console.cloud.google.com/apis/credentials",
      step3: "Click on your OAuth 2.0 Client ID",
      step4: "Add the callbackUrl to 'Authorized redirect URIs'",
      step5: "Click SAVE and wait 1-2 minutes",
    },
  });
}

