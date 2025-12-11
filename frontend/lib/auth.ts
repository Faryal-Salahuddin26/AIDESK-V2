/**
 * Authentication utilities for managing user sessions and tokens
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface SignupResponse {
  success: boolean;
  user: User;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface AuthError {
  error: string;
  detail?: string;
}

/**
 * Sign up a new user
 */
export async function signup(email: string, password: string): Promise<SignupResponse> {
  const response = await fetch(`${API_URL}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    const error: AuthError = {
      error: data.detail || data.error || "Failed to create account",
      detail: data.detail,
    };
    throw error;
  }

  return data as SignupResponse;
}

/**
 * Login with email and password
 */
export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    const error: AuthError = {
      error: data.detail || data.error || "Invalid credentials",
      detail: data.detail,
    };
    throw error;
  }

  return data as LoginResponse;
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User | null> {
  const token = localStorage.getItem("token");
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      return null;
    }

    const user = await response.json();
    localStorage.setItem("user", JSON.stringify(user));
    return user as User;
  } catch (error) {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    return null;
  }
}

/**
 * Save authentication data to localStorage
 */
export function saveAuth(token: string, user: User): void {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}

/**
 * Clear authentication data from localStorage
 */
export function clearAuth(): void {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

/**
 * Get stored token
 */
export function getToken(): string | null {
  return localStorage.getItem("token");
}

/**
 * Get stored user
 */
export function getStoredUser(): User | null {
  const userStr = localStorage.getItem("user");
  if (!userStr) return null;
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

