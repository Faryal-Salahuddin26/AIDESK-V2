import Link from "next/link";
import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryGrid } from "@/components/CategoryGrid";
import { TrendingTicker } from "@/components/trending-ticker";
import { Pagination } from "@/components/pagination";
import { Sparkles, TrendingUp, Clock, ArrowRight, AlertCircle } from "lucide-react";
import { Metadata } from "next";

// Revalidate every 5 minutes
export const revalidate = 300;

export const metadata: Metadata = {
  title: "Latest AI News & Breakthroughs",
  description: "Stay ahead with the latest AI breakthroughs, tools, research, and industry insights. Curated by AI, for the future.",
  openGraph: {
    title: "AI DESK - Latest AI News & Breakthroughs",
    description: "Stay ahead with the latest AI breakthroughs, tools, research, and industry insights.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "AI DESK - Latest AI News & Breakthroughs",
    description: "Stay ahead with the latest AI breakthroughs, tools, research, and industry insights.",
  },
};

interface Article {
  title: string;
  slug: string;
  short_summary: string;
  source: string;
  published_at?: string;
  thumbnail?: string;
  meta_title?: string;
  meta_description?: string;
  tags?: string[];
}

async function getArticles(page: number = 1, limit: number = 10): Promise<{ articles: Article[]; total: number }> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const response = await fetch(
      `${apiUrl}/list-news?page=${page}&limit=${limit}`,
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        cache: 'no-store',
        signal: controller.signal,
      }
    );
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      // Only log unexpected errors (not connection refused)
      if (process.env.NODE_ENV === 'development' && response.status !== 0) {
        console.warn(`⚠️ API returned ${response.status}: ${response.statusText}`);
      }
      return { articles: [], total: 0 };
    }
    
    const data = await response.json();
    
    // Handle response format
    let articles: Article[] = [];
    let total = 0;
    
    if (Array.isArray(data)) {
      articles = data;
      total = data.length;
    } else if (data.articles && Array.isArray(data.articles)) {
      articles = data.articles;
      total = data.total || data.count || articles.length;
    }
    
    // Normalize article fields - map description to short_summary if needed
    articles = articles.map((article: any) => ({
      ...article,
      short_summary: article.short_summary || article.description || '',
      slug: article.slug || article.title?.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 100) || `article-${Date.now()}`,
    }));
    
    return { articles, total };
  } catch (error: any) {
    // Handle network errors gracefully - suppress expected connection errors
    if (error.name === 'AbortError' || error.name === 'TypeError') {
      // Silently handle connection refused errors (backend not running)
      // This is expected behavior and doesn't need to be logged
      return { articles: [], total: 0 };
    } else {
      // Only log unexpected errors
      if (process.env.NODE_ENV === 'development') {
        console.error("❌ Error fetching articles:", error.message);
      }
    }
    return { articles: [], total: 0 };
  }
}

function formatTimeAgo(dateString?: string): string {
  if (!dateString) return "Recently";
  
  const now = new Date();
  const published = new Date(dateString);
  const diffInSeconds = Math.floor((now.getTime() - published.getTime()) / 1000);
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);
  
  if (diffInMinutes < 1) return "Just now";
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  if (diffInHours < 24) return `${diffInHours}h ago`;
  if (diffInDays < 7) return `${diffInDays}d ago`;
  
  return published.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: published.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
  });
}

function FeaturedArticleSkeleton() {
  return (
    <Card className="overflow-hidden border-border/50">
      <Skeleton className="h-64 md:h-96 w-full" />
      <CardContent className="p-6 space-y-4">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-3/4" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-10 w-32" />
      </CardContent>
    </Card>
  );
}

function MediumCardSkeleton() {
  return (
    <Card className="overflow-hidden border-border/50 h-full">
      <Skeleton className="h-48 w-full" />
      <CardContent className="p-5 space-y-3">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-4/5" />
        <Skeleton className="h-16 w-full" />
      </CardContent>
    </Card>
  );
}

function SmallCardSkeleton() {
  return (
    <Card className="overflow-hidden border-border/50 h-full">
      <Skeleton className="h-40 w-full" />
      <CardContent className="p-4 space-y-2">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-5 w-full" />
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-12 w-full" />
      </CardContent>
    </Card>
  );
}

function FeaturedArticle({ article }: { article: Article }) {
  return (
    <Link href={`/news/${article.slug}`} className="block group">
      <Card className="overflow-hidden transition-all duration-500 hover:shadow-2xl hover:-translate-y-2 border-border/50 bg-card hover:border-primary/30">
        <div className="relative h-64 md:h-96 w-full overflow-hidden">
          {article.thumbnail ? (
            <Image
              src={article.thumbnail}
              alt={article.title}
              fill
              className="object-cover transition-transform duration-700 group-hover:scale-110"
              sizes="(max-width: 768px) 100vw, 100vw"
              priority
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-primary/20 via-purple-500/20 to-pink-500/20 flex items-center justify-center group-hover:from-primary/30 group-hover:via-purple-500/30 transition-all duration-500">
              <Sparkles className="h-24 w-24 text-primary/50 group-hover:text-primary/70 transition-colors" />
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-background/95 via-background/60 to-transparent group-hover:from-background/98 transition-all duration-500" />
        </div>
        <CardContent className="p-6 md:p-8 space-y-4 relative -mt-20 md:-mt-24">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 group-hover:bg-primary/20 transition-colors">
              {article.source}
            </Badge>
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              <time dateTime={article.published_at}>{formatTimeAgo(article.published_at)}</time>
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold leading-tight group-hover:text-primary transition-colors duration-300">
            {article.title}
          </h1>
          {article.short_summary && (
            <p className="text-base md:text-lg text-muted-foreground line-clamp-3 leading-relaxed">
              {article.short_summary}
            </p>
          )}
          <div className="flex items-center gap-2 text-primary font-semibold group-hover:gap-3 transition-all duration-300">
            <span>Read More</span>
            <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function MediumCard({ article }: { article: Article }) {
  return (
    <Link href={`/news/${article.slug}`} className="block h-full group">
      <Card className="h-full overflow-hidden transition-all duration-500 hover:shadow-xl hover:-translate-y-2 border-border/50 bg-card hover:border-primary/30">
        <div className="relative h-48 w-full overflow-hidden">
          {article.thumbnail ? (
            <Image
              src={article.thumbnail}
              alt={article.title}
              fill
              className="object-cover transition-transform duration-700 group-hover:scale-110"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 33vw, 33vw"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-primary/20 via-purple-500/20 to-pink-500/20 flex items-center justify-center group-hover:from-primary/30 group-hover:via-purple-500/30 transition-all duration-500">
              <Sparkles className="h-16 w-16 text-primary/50 group-hover:text-primary/70 transition-colors" />
            </div>
          )}
        </div>
        <CardContent className="p-5 space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 text-xs group-hover:bg-primary/20 transition-colors">
              {article.source}
            </Badge>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <time dateTime={article.published_at}>{formatTimeAgo(article.published_at)}</time>
            </div>
          </div>
          <h2 className="text-xl md:text-2xl font-bold leading-tight line-clamp-2 group-hover:text-primary transition-colors duration-300">
            {article.title}
          </h2>
          {article.short_summary && (
            <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
              {article.short_summary}
            </p>
          )}
          <div className="flex items-center gap-2 text-sm text-primary font-medium opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:gap-3">
            <span>Read More</span>
            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function SmallCard({ article }: { article: Article }) {
  return (
    <Link href={`/news/${article.slug}`} className="block h-full group">
      <Card className="h-full overflow-hidden transition-all duration-500 hover:shadow-lg hover:-translate-y-1 border-border/50 bg-card hover:border-primary/30">
        <div className="relative h-40 w-full overflow-hidden">
          {article.thumbnail ? (
            <Image
              src={article.thumbnail}
              alt={article.title}
              fill
              className="object-cover transition-transform duration-700 group-hover:scale-110"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-primary/20 via-purple-500/20 to-pink-500/20 flex items-center justify-center group-hover:from-primary/30 group-hover:via-purple-500/30 transition-all duration-500">
              <Sparkles className="h-12 w-12 text-primary/50 group-hover:text-primary/70 transition-colors" />
            </div>
          )}
        </div>
        <CardContent className="p-4 space-y-2">
          <div className="flex items-center justify-between flex-wrap gap-1">
            <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 text-xs px-2 py-0.5 group-hover:bg-primary/20 transition-colors">
              {article.source}
            </Badge>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <time dateTime={article.published_at}>{formatTimeAgo(article.published_at)}</time>
            </div>
          </div>
          <h3 className="text-base font-bold leading-tight line-clamp-2 group-hover:text-primary transition-colors duration-300">
            {article.title}
          </h3>
          {article.short_summary && (
            <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
              {article.short_summary}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}

function EmptyState() {
  return (
    <div className="py-20 text-center">
      <div className="max-w-md mx-auto space-y-6 animate-fade-in">
        <div className="relative mx-auto w-24 h-24">
          <div className="absolute inset-0 bg-primary/20 blur-2xl rounded-full animate-pulse"></div>
          <div className="relative bg-card border border-border/50 rounded-full p-6">
            <AlertCircle className="h-12 w-12 text-primary" />
          </div>
        </div>
        <div>
          <h3 className="text-2xl font-bold mb-2">No Articles Available</h3>
          <p className="text-muted-foreground mb-6">
            News articles are being collected automatically. Please check back soon!
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <TrendingUp className="h-4 w-4 animate-pulse" />
            <span>Collecting latest AI news...</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const resolvedSearchParams = await searchParams;
  const currentPage = parseInt(resolvedSearchParams?.page || "1", 10);
  const limit = 10;
  const { articles, total } = await getArticles(currentPage, limit);
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border/50">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-purple-500/5 to-pink-500/5 pointer-events-none"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(99,102,241,0.1),transparent_50%)] pointer-events-none"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(168,85,247,0.1),transparent_50%)] pointer-events-none"></div>
        
        <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-12 sm:py-16 lg:py-20">
          <div className="max-w-4xl mx-auto text-center space-y-6 animate-fade-in">
            <div className="flex items-center justify-center gap-2 sm:gap-3 mb-4">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/30 blur-2xl rounded-full animate-pulse pointer-events-none"></div>
                <div className="relative bg-gradient-to-br from-primary to-purple-500 p-2 sm:p-3 rounded-xl shadow-lg shadow-primary/20">
                  <Sparkles className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
                </div>
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
                AI DESK
              </h1>
            </div>
            
            <div className="space-y-3">
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight">
                <span className="text-foreground">Your Window to the</span>
                <br />
                <span className="bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
                  Future of AI
                </span>
              </h2>
              
              <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Stay ahead with the latest AI breakthroughs, tools, research, and industry insights.
                <span className="text-primary font-medium"> Curated by AI, for the future.</span>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="border-b border-border/50 bg-gradient-to-b from-background to-muted/20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-12">
          <div className="mb-8 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-4">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-semibold text-primary">Explore</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-3">Browse by Category</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Discover AI news organized by topics that matter to you
            </p>
          </div>
          <CategoryGrid />
        </div>
      </section>

      {/* Main News Section - CoinDesk Style */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-12">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-3xl lg:text-4xl font-bold">Latest News</h2>
          </div>
        </div>

        {articles.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-8">
            {/* Featured Article - Big Card */}
            {articles[0] && (
              <div>
                <FeaturedArticle article={articles[0]} />
              </div>
            )}

            {/* Medium Cards - 3 Cards */}
            {articles.length > 1 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {articles.slice(1, 4).map((article) => (
                  <MediumCard key={article.slug} article={article} />
                ))}
              </div>
            )}

            {/* Small Cards Grid - 6 Cards */}
            {articles.length > 4 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
                {articles.slice(4, 10).map((article) => (
                  <SmallCard key={article.slug} article={article} />
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-12">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  baseUrl="/"
                />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
