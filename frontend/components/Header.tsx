"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Menu, X, Sparkles } from "lucide-react";
import { useState } from "react";
import { ThemeToggle } from "./theme-toggle";
import { usePathname } from "next/navigation";

const categories = [
  { name: "Home", href: "/" },
  { name: "AI Tools", href: "/category/ai-tools" },
  { name: "Research", href: "/category/research" },
  { name: "Industry", href: "/category/industry" },
  { name: "Startups", href: "/category/startups" },
  { name: "Models", href: "/category/models" },
  { name: "Breakthroughs", href: "/category/breakthroughs" },
];

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/95 backdrop-blur-xl supports-[backdrop-filter]:bg-background/80 shadow-sm">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group flex-shrink-0">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-lg rounded-full group-hover:bg-primary/30 transition-colors"></div>
              <div className="relative bg-gradient-to-br from-primary to-purple-500 p-1.5 rounded-lg">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent whitespace-nowrap">
              AI DESK
            </span>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1">
            {categories.map((category) => {
              const isActive = pathname === category.href || 
                (category.href !== "/" && pathname?.startsWith(category.href));
              
              return (
                <Link 
                  key={category.href}
                  href={category.href} 
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 whitespace-nowrap ${
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  {category.name}
                </Link>
              );
            })}
          </nav>
          
          {/* Right Side Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <ThemeToggle />
            
            <div className="hidden md:flex items-center gap-2">
              <Link href="/login">
                <Button variant="ghost" size="sm" className="hover:bg-muted">
                  Sign In
                </Button>
              </Link>
              <Link href="/signup">
                <Button 
                  size="sm" 
                  className="bg-gradient-to-r from-primary to-purple-500 hover:shadow-lg hover:scale-105 transition-all duration-200"
                >
                  Sign Up
                </Button>
              </Link>
            </div>
            
            {/* Mobile Menu Button */}
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-muted transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
        
        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-border/50 py-4 space-y-2 animate-in slide-in-from-top">
            <nav className="flex flex-col space-y-1">
              {categories.map((category) => {
                const isActive = pathname === category.href || 
                  (category.href !== "/" && pathname?.startsWith(category.href));
                
                return (
                  <Link 
                    key={category.href}
                    href={category.href} 
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "hover:bg-muted"
                    }`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {category.name}
                  </Link>
                );
              })}
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
