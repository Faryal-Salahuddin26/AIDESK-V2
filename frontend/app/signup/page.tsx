"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles, AlertCircle, Loader2 } from "lucide-react";
import { signup, saveAuth } from "@/lib/auth";
import { useToast } from "@/components/ui/toast";

export default function SignUpPage() {
  const router = useRouter();
  const toast = useToast();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData({
      ...formData,
      [id]: value,
    });
    // Clear error for this field when user types
    if (errors[id]) {
      setErrors({
        ...errors,
        [id]: "",
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Invalid email format";
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters long";
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    // Terms validation
    if (!acceptedTerms) {
      newErrors.terms = "Please accept the terms and conditions";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await signup(formData.email, formData.password);

      if (response.success) {
        // After signup, automatically login
        try {
          const loginResponse = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/login`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                email: formData.email,
                password: formData.password,
              }),
            }
          );

          const loginData = await loginResponse.json();

          if (loginResponse.ok && loginData.token) {
            saveAuth(loginData.token, loginData.user);
            toast.success("Account created successfully!", "Welcome to AI DESK");
            router.push("/dashboard");
          } else {
            toast.success("Account created successfully!", "Please sign in to continue");
            router.push("/login");
          }
        } catch (loginError) {
          toast.success("Account created successfully!", "Please sign in to continue");
          router.push("/login");
        }
      }
    } catch (error: any) {
      console.error("Signup error:", error);
      
      // Handle different error types
      if (error.error) {
        const errorMessage = error.error.toLowerCase();
        
        if (errorMessage.includes("email already") || errorMessage.includes("already registered")) {
          setErrors({ email: "Email already registered" });
          toast.error("Signup failed", "This email is already registered");
        } else if (errorMessage.includes("password") && errorMessage.includes("8")) {
          setErrors({ password: "Password must be at least 8 characters long" });
          toast.error("Signup failed", "Password must be at least 8 characters long");
        } else if (errorMessage.includes("invalid email")) {
          setErrors({ email: "Invalid email format" });
          toast.error("Signup failed", "Please enter a valid email address");
        } else {
          toast.error("Signup failed", error.error || "Failed to create account. Please try again.");
        }
      } else {
        toast.error("Signup failed", "An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
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
          {/* Error Message */}
          {Object.keys(errors).length > 0 && (
            <div className="flex items-start gap-2 p-3 sm:p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                {Object.values(errors).map((error, index) => (
                  <div key={index}>{error}</div>
                ))}
              </div>
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
                disabled={loading}
                className={`h-10 sm:h-11 text-sm sm:text-base ${
                  errors.email ? "border-destructive focus-visible:ring-destructive" : ""
                }`}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email}</p>
              )}
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
                disabled={loading}
                className={`h-10 sm:h-11 text-sm sm:text-base ${
                  errors.password ? "border-destructive focus-visible:ring-destructive" : ""
                }`}
              />
              {errors.password && (
                <p className="text-sm text-destructive">{errors.password}</p>
              )}
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
                disabled={loading}
                className={`h-10 sm:h-11 text-sm sm:text-base ${
                  errors.confirmPassword ? "border-destructive focus-visible:ring-destructive" : ""
                }`}
              />
              {errors.confirmPassword && (
                <p className="text-sm text-destructive">{errors.confirmPassword}</p>
              )}
            </div>
            <div className="flex items-start gap-2 sm:gap-3">
              <input
                type="checkbox"
                id="terms"
                checked={acceptedTerms}
                onChange={(e) => {
                  setAcceptedTerms(e.target.checked);
                  if (errors.terms) {
                    setErrors({ ...errors, terms: "" });
                  }
                }}
                disabled={loading}
                className="mt-1 h-4 w-4 rounded border-border text-primary focus:ring-primary focus:ring-offset-0 cursor-pointer"
              />
              <label htmlFor="terms" className="text-xs sm:text-sm text-muted-foreground leading-relaxed cursor-pointer">
                I agree to receive updates and offers from AI DESK and its affiliates or third parties (opt out anytime)
              </label>
            </div>
            {errors.terms && (
              <p className="text-sm text-destructive">{errors.terms}</p>
            )}
            <Button
              type="submit"
              disabled={loading || !acceptedTerms}
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
