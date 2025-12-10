"use client";

import Link from "next/link";
import { 
  Wrench, 
  Microscope, 
  Building2, 
  Rocket, 
  Bot, 
  Lightbulb,
  ArrowRight
} from "lucide-react";
import { cn } from "@/lib/utils";

const CATEGORIES = [
  {
    slug: "ai-tools",
    name: "AI Tools",
    icon: Wrench,
    color: "text-yellow-500",
    bgColor: "bg-yellow-500/10",
    borderColor: "border-yellow-500/20",
    hoverColor: "hover:bg-yellow-500/20",
    description: "Latest AI tools and platforms",
  },
  {
    slug: "research",
    name: "Research",
    icon: Microscope,
    color: "text-white",
    bgColor: "bg-white/10",
    borderColor: "border-white/20",
    hoverColor: "hover:bg-white/20",
    description: "Cutting-edge AI research",
  },
  {
    slug: "industry",
    name: "Industry",
    icon: Building2,
    color: "text-blue-400",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/20",
    hoverColor: "hover:bg-blue-500/20",
    description: "Industry news and insights",
  },
  {
    slug: "startups",
    name: "Startups",
    icon: Rocket,
    color: "text-red-500",
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/20",
    hoverColor: "hover:bg-red-500/20",
    description: "AI startups and funding",
  },
  {
    slug: "models",
    name: "Models",
    icon: Bot,
    color: "text-gray-400",
    bgColor: "bg-gray-500/10",
    borderColor: "border-gray-500/20",
    hoverColor: "hover:bg-gray-500/20",
    description: "New AI models and releases",
  },
  {
    slug: "breakthroughs",
    name: "Breakthroughs",
    icon: Lightbulb,
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/10",
    borderColor: "border-yellow-500/20",
    hoverColor: "hover:bg-yellow-500/20",
    description: "Major AI breakthroughs",
  },
];

export function CategoryGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
      {CATEGORIES.map((category) => {
        const Icon = category.icon;
        return (
          <Link
            key={category.slug}
            href={`/category/${category.slug}`}
            className={cn(
              "group relative overflow-hidden rounded-xl sm:rounded-2xl border bg-card p-4 sm:p-5 lg:p-6 transition-all duration-300",
              "hover:shadow-xl hover:shadow-primary/10 hover:-translate-y-1",
              category.bgColor,
              category.borderColor,
              category.hoverColor
            )}
          >
            <div className="flex items-start gap-3 sm:gap-4 mb-3 sm:mb-4">
              <div className={cn(
                "p-3 rounded-xl transition-all duration-300 border",
                category.bgColor,
                category.borderColor,
                "group-hover:scale-110 group-hover:shadow-lg"
              )}>
                <Icon className={cn("h-6 w-6", category.color)} />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-1 group-hover:text-primary transition-colors">
                  {category.name}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {category.description}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2 text-sm text-primary font-medium opacity-0 group-hover:opacity-100 transition-opacity">
              <span>Explore</span>
              <ArrowRight className="h-4 w-4" />
            </div>
            
            {/* Hover effect */}
            <div className={cn(
              "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300",
              "bg-gradient-to-br from-primary/5 via-transparent to-transparent"
            )} />
          </Link>
        );
      })}
    </div>
  );
}
