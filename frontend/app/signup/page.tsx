"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signIn } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles, AlertCircle, Loader2, Check } from "lucide-react";

export default function SignUpPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
    setError("");
  };

  const validateForm = () => {
    if (!formData.email || !formData.password || !formData.confirmPassword) {
      setError("Please fill in all fields.");
      return false;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return false;
    }

    if (!acceptedTerms) {
      setError("Please accept the terms and conditions.");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // TODO: Replace with actual API call to your backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      if (response.ok) {
        // Auto sign in after registration
        const result = await signIn("credentials", {
          email: formData.email,
          password: formData.password,
          redirect: false,
        });

        if (result?.ok) {
          router.push("/");
          router.refresh();
        } else {
          setError("Account created but sign in failed. Please try signing in.");
        }
      } else {
        const data = await response.json();
        setError(data.message || "Failed to create account. Please try again.");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthSignIn = async (provider: "google" | "apple") => {
    setError("");
    setOauthLoading(provider);

    try {
      await signIn(provider, {
        callbackUrl: "/",
        redirect: true,
      });
    } catch (err) {
      setError(`Failed to sign in with ${provider}. Please try again.`);
      setOauthLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      <Card className="w-full max-w-md border-border/50 shadow-xl">
        <CardHeader className="space-y-3 sm:space-y-4 px-4 sm:px-6 pt-6 sm:pt-8">
          <div className="flex items-center justify-center mb-2 sm:mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-lg rounded-full"></div>
              <div className="relative bg-gradient-to-br from-primary to-purple-500 p-2 sm:p-2.5 rounded-lg">
                <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
              </div>
            </div>
            <h1 className="ml-2 sm:ml-3 text-2xl sm:text-3xl font-bold bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
              AI DESK
            </h1>
          </div>
          <CardTitle className="text-xl sm:text-2xl text-center font-bold">
            Create Your Account
          </CardTitle>
          <CardDescription className="text-center text-sm sm:text-base">
            Sign up to get started with AI DESK
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 sm:space-y-5 px-4 sm:px-6 pb-6 sm:pb-8">
          {/* OAuth Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <Button
              variant="outline"
              type="button"
              onClick={() => handleOAuthSignIn("google")}
              disabled={loading || oauthLoading !== null}
              className="w-full h-10 sm:h-11 text-sm sm:text-base border-border/50 hover:bg-muted/50 transition-all"
            >
              {oauthLoading === "google" ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <svg className="mr-2 h-4 w-4 flex-shrink-0" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
              )}
              <span className="truncate">Google</span>
            </Button>
            <Button
              variant="outline"
              type="button"
              onClick={() => handleOAuthSignIn("apple")}
              disabled={loading || oauthLoading !== null}
              className="w-full h-10 sm:h-11 text-sm sm:text-base border-border/50 hover:bg-muted/50 transition-all"
            >
              {oauthLoading === "apple" ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <svg className="mr-2 h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-5.18 3.014-2.2 3.817-.546 9.412 1.579 12.507 1.094 1.579 2.387 3.352 4.078 3.287 1.633-.07 2.25-1.06 4.22-1.06 1.969 0 2.523 1.06 4.22 1.03 1.78-.03 2.87-1.603 3.96-3.188 1.245-1.817 1.757-3.574 1.787-3.664-.039-.013-3.422-1.313-3.457-5.208-.033-3.287 2.679-4.864 2.789-4.94-1.523-2.26-3.89-2.51-4.828-2.56-2.04-.156-3.757 1.183-4.72 1.183zm-.83-5.277c1.235-.82 3.08-1.377 4.867-1.377.052 0 .105 0 .157.001-1.1 2.614-.842 4.95-.642 6.29.016.092.03.184.047.276.12-.405.26-.798.42-1.18-1.62-.61-3.04-1.61-4.19-2.81-.75-.8-1.4-1.74-1.92-2.75-.52-1.01-.9-2.08-1.13-3.19z"/>
                </svg>
              )}
              <span className="truncate">Apple</span>
            </Button>
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-border/50" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 sm:px-3 text-muted-foreground text-xs sm:text-sm">
                Or sign up with email
              </span>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 sm:p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Registration Form */}
          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm sm:text-base font-medium">
                Email address <span className="text-destructive">*</span>
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={loading || oauthLoading !== null}
                className="h-10 sm:h-11 text-sm sm:text-base"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm sm:text-base font-medium">
                Password <span className="text-destructive">*</span>
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="Create a password (min. 8 characters)"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={loading || oauthLoading !== null}
                className="h-10 sm:h-11 text-sm sm:text-base"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm sm:text-base font-medium">
                Confirm Password <span className="text-destructive">*</span>
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                disabled={loading || oauthLoading !== null}
                className="h-10 sm:h-11 text-sm sm:text-base"
              />
            </div>
            <div className="flex items-start gap-2 sm:gap-3">
              <input
                type="checkbox"
                id="terms"
                checked={acceptedTerms}
                onChange={(e) => setAcceptedTerms(e.target.checked)}
                disabled={loading || oauthLoading !== null}
                className="mt-1 h-4 w-4 rounded border-border text-primary focus:ring-primary focus:ring-offset-0 cursor-pointer"
              />
              <label htmlFor="terms" className="text-xs sm:text-sm text-muted-foreground leading-relaxed cursor-pointer">
                I agree to receive updates and offers from AI DESK and its affiliates or third parties (opt out anytime)
              </label>
            </div>
            <Button
              type="submit"
              disabled={loading || oauthLoading !== null || !acceptedTerms}
              className="w-full h-10 sm:h-11 text-sm sm:text-base bg-gradient-to-r from-primary to-purple-500 hover:shadow-lg transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                "Create Account"
              )}
            </Button>
          </form>

          {/* Terms and Privacy */}
          <div className="text-center text-xs sm:text-sm text-muted-foreground leading-relaxed">
            By creating an account, you agree to AI DESK's{" "}
            <Link href="/terms" className="text-primary hover:underline font-medium">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="/privacy" className="text-primary hover:underline font-medium">
              Privacy Policy
            </Link>
            .
          </div>

          {/* Sign In Link */}
          <div className="text-center text-sm sm:text-base pt-2">
            <span className="text-muted-foreground">Already have an account? </span>
            <Link href="/login" className="text-primary hover:underline font-medium">
              Sign in
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
