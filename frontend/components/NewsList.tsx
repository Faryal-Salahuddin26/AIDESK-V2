"use client";

import { useState, useEffect } from "react";
import { NewsCard } from "./NewsCard";
import { RefreshCw, AlertCircle } from "lucide-react";

interface Article {
  title: string;
  slug: string;
  short_summary: string;
  source: string;
  published_at?: string;
  thumbnail?: string;
}

interface NewsListProps {
  initialArticles?: Article[];
}

export function NewsList({ initialArticles = [] }: NewsListProps) {
  const [articles, setArticles] = useState<Article[]>(initialArticles);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = async () => {
    setLoading(true);
    setError(null);
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    
    try {
      // Try new API endpoint
      let response = await fetch(
        `${apiUrl}/api/v1/list-news?page=1&limit=30`,
        {
          cache: 'no-store',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        }
      );
      
      // Try fallback endpoint if first fails
      if (!response.ok) {
        response = await fetch(
          `${apiUrl}/list-news`,
          {
            cache: 'no-store',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          }
        );
      }
      
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      
      const data = await response.json();
      
      // Handle multiple response formats
      let articlesData: Article[] = [];
      if (Array.isArray(data)) {
        articlesData = data;
      } else if (data.articles && Array.isArray(data.articles)) {
        articlesData = data.articles;
      }
      
      setArticles(articlesData);
    } catch (err: any) {
      console.error("Error fetching articles:", err);
      setError(err.message || "Failed to load articles");
      // Keep initial articles if available
      if (initialArticles.length > 0) {
        setArticles(initialArticles);
      }
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchArticles();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

  if (loading && articles.length === 0) {
    return (
      <div className="py-20 text-center">
        <div className="max-w-md mx-auto space-y-6">
          <RefreshCw className="h-12 w-12 text-primary mx-auto animate-spin" />
          <div>
            <h3 className="text-xl font-semibold mb-2">Loading News</h3>
            <p className="text-muted-foreground">
              Fetching the latest AI articles...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error && articles.length === 0) {
    return (
      <div className="py-20 text-center">
        <div className="max-w-md mx-auto space-y-6">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
          <div>
            <h3 className="text-xl font-semibold mb-2">Unable to Load News</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
            <button
              onClick={fetchArticles}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="py-20 text-center">
        <div className="max-w-md mx-auto space-y-6">
          <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto" />
          <div>
            <h3 className="text-xl font-semibold mb-2">No Articles Available</h3>
            <p className="text-muted-foreground mb-4">
              News articles are being collected automatically. Please check back soon!
            </p>
            <button
              onClick={fetchArticles}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2 mx-auto"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {articles.map((article, idx) => (
        <NewsCard
          key={article.slug || `article-${idx}`}
          title={article.title}
          slug={article.slug || `article-${idx}`}
          short_summary={article.short_summary || ""}
          source={article.source}
          published_at={article.published_at}
          thumbnail={article.thumbnail}
          variant="horizontal"
        />
      ))}
    </div>
  );
}

