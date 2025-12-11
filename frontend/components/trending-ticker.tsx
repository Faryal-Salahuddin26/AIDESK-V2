"use client";

import { useEffect, useState } from "react";
import { TrendingUp } from "lucide-react";
import Link from "next/link";

interface TrendingTickerProps {
  articles?: Array<{ title: string; slug: string }>;
}

export function TrendingTicker({ articles = [] }: TrendingTickerProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Use first 5 articles as trending
  const trendingItems = articles.slice(0, 5);

  if (!mounted || trendingItems.length === 0) {
    return null;
  }

  return (
    <div className="border-b border-border/50 bg-muted/30 py-2 overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 flex-shrink-0">
            <TrendingUp className="h-4 w-4 text-primary animate-pulse" />
            <span className="text-xs font-semibold text-primary uppercase tracking-wide">
              Trending
            </span>
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="flex gap-6 animate-scroll">
              {[...trendingItems, ...trendingItems].map((article, idx) => (
                <Link
                  key={`${article.slug}-${idx}`}
                  href={`/news/${article.slug}`}
                  className="text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors whitespace-nowrap flex-shrink-0"
                >
                  {article.title}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
      <style jsx>{`
        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        .animate-scroll {
          animation: scroll 30s linear infinite;
        }
        .animate-scroll:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
}

