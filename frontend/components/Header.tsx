"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Menu, X, Sparkles } from "lucide-react";
import { useState } from "react";

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/95 backdrop-blur-xl supports-[backdrop-filter]:bg-background/80 shadow-sm">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="flex h-14 sm:h-16 items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 sm:gap-2.5 group flex-shrink-0">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-lg rounded-full group-hover:bg-primary/30 transition-colors"></div>
              <div className="relative bg-gradient-to-br from-primary to-purple-500 p-1 sm:p-1.5 rounded-lg">
                <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
              </div>
            </div>
            <span className="text-lg sm:text-xl font-bold bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent whitespace-nowrap">
              AI DESK
            </span>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1 flex-wrap">
            <Link 
              href="/" 
              className="px-3 xl:px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-all duration-200 hover:text-primary whitespace-nowrap"
            >
              Home
            </Link>
            <Link 
              href="/category/ai-tools" 
              className="px-3 xl:px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-all duration-200 hover:text-primary whitespace-nowrap"
            >
              AI Tools
            </Link>
            <Link 
              href="/category/research" 
              className="px-3 xl:px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-all duration-200 hover:text-primary whitespace-nowrap"
            >
              Research
            </Link>
            <Link 
              href="/category/industry" 
              className="px-3 xl:px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-all duration-200 hover:text-primary whitespace-nowrap"
            >
              Industry
            </Link>
            <Link 
              href="/category/startups" 
              className="px-3 xl:px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-all duration-200 hover:text-primary whitespace-nowrap"
            >
              Startups
            </Link>
            <Link 
              href="/category/models" 
              className="px-3 xl:px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-all duration-200 hover:text-primary whitespace-nowrap"
            >
              Models
            </Link>
            <Link 
              href="/category/breakthroughs" 
              className="px-3 xl:px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-all duration-200 hover:text-primary whitespace-nowrap"
            >
              Breakthroughs
            </Link>
          </nav>
          
          {/* Auth Buttons */}
          <div className="hidden md:flex items-center gap-2 lg:gap-3 flex-shrink-0">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="hover:bg-muted text-xs sm:text-sm">
                Sign In
              </Button>
            </Link>
            <Link href="/signup">
              <Button 
                size="sm" 
                className="bg-gradient-to-r from-primary to-purple-500 hover:shadow-lg hover:scale-105 transition-all duration-200 text-xs sm:text-sm"
              >
                Sign Up
              </Button>
            </Link>
          </div>
          
          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-muted transition-colors flex-shrink-0"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5 sm:h-6 sm:w-6" /> : <Menu className="h-5 w-5 sm:h-6 sm:w-6" />}
          </button>
        </div>
        
        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-border/50 py-4 space-y-2 animate-in slide-in-from-top">
            <nav className="flex flex-col space-y-1">
              <Link 
                href="/" 
                className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Home
              </Link>
              <Link 
                href="/category/ai-tools" 
                className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-colors flex items-center gap-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="text-yellow-500">🔧</span> AI Tools
              </Link>
              <Link 
                href="/category/research" 
                className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-colors flex items-center gap-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="text-white">🔬</span> Research
              </Link>
              <Link 
                href="/category/industry" 
                className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-colors flex items-center gap-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="text-blue-400">🏢</span> Industry
              </Link>
              <Link 
                href="/category/startups" 
                className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-colors flex items-center gap-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="text-red-500">🚀</span> Startups
              </Link>
              <Link 
                href="/category/models" 
                className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-colors flex items-center gap-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="text-gray-400">🤖</span> Models
              </Link>
              <Link 
                href="/category/breakthroughs" 
                className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-muted transition-colors flex items-center gap-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="text-yellow-400">💡</span> Breakthroughs
              </Link>
            </nav>
            <div className="flex flex-col gap-2 pt-4 border-t">
              <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="outline" className="w-full">Sign In</Button>
              </Link>
              <Link href="/signup" onClick={() => setMobileMenuOpen(false)}>
                <Button className="w-full bg-gradient-to-r from-primary to-purple-500">
                  Sign Up
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
