import { NewsCard } from "@/components/NewsCard";
import { CategoryGrid } from "@/components/CategoryGrid";
import Link from "next/link";
import { Sparkles, TrendingUp, Zap, RefreshCw, AlertCircle } from "lucide-react";

// Revalidate every 5 minutes to show fresh news
export const revalidate = 300;

async function getArticles() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  // Log API URL for debugging (only in development)
  if (process.env.NODE_ENV === 'development') {
    console.log("🔍 Fetching articles from:", `${apiUrl}/api/v1/list-news`);
  }
  
  try {
    // Try primary endpoint with /api/v1 prefix
    let response = await fetch(
      `${apiUrl}/api/v1/list-news?page=1&limit=50`,
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        cache: 'no-store', // Force fresh data (removed conflicting revalidate)
      }
    );
    
    // If 404, try endpoint without /api/v1 prefix (for old backend)
    if (!response.ok && response.status === 404) {
      console.log("⚠️ /api/v1/list-news not found, trying /list-news...");
      response = await fetch(
        `${apiUrl}/list-news?page=1&limit=50`,
        {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          cache: 'no-store', // Force fresh data
        }
      );
    }
    
    if (!response.ok) {
      console.error(`❌ API Error: ${response.status} ${response.statusText}`);
      console.error(`URL tried: ${apiUrl}/api/v1/list-news and ${apiUrl}/list-news`);
      return [];
    }
    
    const data = await response.json();
    
    // Handle different response formats
    let articles: any[] = [];
    
    if (Array.isArray(data)) {
      articles = data;
      console.log(`✅ API returned ${articles.length} articles (array format)`);
    } else if (data.articles && Array.isArray(data.articles)) {
      articles = data.articles;
      console.log(`✅ API returned ${articles.length} articles (object format)`);
    } else {
      console.warn("⚠️ Unexpected response format:", Object.keys(data));
      console.warn("Response data:", JSON.stringify(data).substring(0, 200));
    }
    
    return articles;
  } catch (error: any) {
    console.error("❌ Error fetching articles:", error.message);
    console.error("API URL:", apiUrl);
    console.error("Error type:", error.name);
    
    // Provide helpful error message
    if (error.message.includes('fetch')) {
      console.error("💡 Tip: Make sure backend is running on http://localhost:8000");
      console.error("   Run: cd backend && uvicorn app.main:app --reload --port 8000");
    }
    
    return [];
  }
}

export default async function Home() {
  const articles = await getArticles();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border/50">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-purple-500/5 to-pink-500/5 pointer-events-none"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(99,102,241,0.1),transparent_50%)] pointer-events-none"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(168,85,247,0.1),transparent_50%)] pointer-events-none"></div>
        
        <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-12 sm:py-16 lg:py-20 xl:py-28">
          <div className="max-w-4xl mx-auto text-center space-y-6 sm:space-y-8 animate-fade-in">
            {/* Logo/Brand */}
            <div className="flex items-center justify-center gap-2 sm:gap-3 mb-4 sm:mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/30 blur-2xl rounded-full animate-pulse pointer-events-none"></div>
                <div className="relative bg-gradient-to-br from-primary to-purple-500 p-2 sm:p-3 rounded-xl sm:rounded-2xl shadow-lg shadow-primary/20">
                  <Sparkles className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
                </div>
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent animate-gradient">
                AI DESK
              </h1>
            </div>
            
            {/* Hero Title */}
            <div className="space-y-3 sm:space-y-4">
              <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight px-2">
                <span className="text-foreground block sm:inline">
                  Your Window to the
                </span>
                <br className="hidden sm:block" />
                <span className="bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent animate-gradient block sm:inline">
                  Future of AI
                </span>
              </h2>
              
              <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed px-4">
                Stay ahead with the latest AI breakthroughs, tools, research, and industry insights. 
                <span className="text-primary font-medium"> Curated by AI, for the future.</span>
              </p>
            </div>
            
            {/* Stats */}
            <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 pt-4 sm:pt-6 px-4">
              <div className="flex items-center gap-2 px-5 py-2.5 bg-card/80 backdrop-blur-sm rounded-full border border-border/50 shadow-sm hover:shadow-md transition-all">
                <div className="p-1.5 bg-primary/10 rounded-lg">
                  <TrendingUp className="h-4 w-4 text-primary" />
                </div>
                <span className="text-sm font-semibold">{articles.length}+ Articles</span>
              </div>
              <div className="flex items-center gap-2 px-5 py-2.5 bg-card/80 backdrop-blur-sm rounded-full border border-border/50 shadow-sm hover:shadow-md transition-all">
                <div className="p-1.5 bg-purple-500/10 rounded-lg">
                  <Zap className="h-4 w-4 text-purple-500" />
                </div>
                <span className="text-sm font-semibold">Auto-Updated</span>
              </div>
              <div className="flex items-center gap-2 px-5 py-2.5 bg-card/80 backdrop-blur-sm rounded-full border border-border/50 shadow-sm hover:shadow-md transition-all">
                <div className="p-1.5 bg-pink-500/10 rounded-lg">
                  <Sparkles className="h-4 w-4 text-pink-500" />
                </div>
                <span className="text-sm font-semibold">AI-Powered</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="border-b border-border/50 bg-gradient-to-b from-background to-muted/20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-12 sm:py-14 lg:py-16">
          <div className="mb-8 sm:mb-10 text-center px-2">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-4">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-semibold text-primary">Explore</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-3">
              Browse by Category
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Discover AI news organized by topics that matter to you
            </p>
          </div>
          <CategoryGrid />
        </div>
      </section>


      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-12 sm:py-14 lg:py-16">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8 sm:mb-10">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="p-1.5 sm:p-2 bg-primary/10 rounded-lg flex-shrink-0">
              <TrendingUp className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
            </div>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold">Latest News</h2>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted/50 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full border border-border/50 whitespace-nowrap">
            <RefreshCw className="h-3 w-3 animate-spin flex-shrink-0" />
            <span className="hidden xs:inline">Auto-updates every 15 min</span>
            <span className="xs:hidden">Auto-updates</span>
          </div>
        </div>

        {articles.length === 0 ? (
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
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Collecting latest AI news...</span>
                </div>
                <p className="text-xs text-muted-foreground mt-4">
                  News is collected automatically every 15 minutes from multiple sources
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5 lg:gap-6">
            {articles
              .filter((article: any) => {
                // Additional client-side filtering for professional AI content
                const title = (article.title || "").toLowerCase();
                const summary = (article.short_summary || article.description || "").toLowerCase();
                const content = `${title} ${summary}`;
                
                const professionalKeywords = [
                  'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
                  'neural network', 'llm', 'gpt', 'openai', 'transformer', 'nlp',
                  'computer vision', 'robotics', 'automation', 'data science', 'algorithm',
                  'research', 'breakthrough', 'innovation', 'technology', 'model',
                  'training', 'inference', 'architecture', 'paper', 'study'
                ];
                
                const excludeKeywords = [
                  'shorts', '#shorts', 'viral', 'trending', 'funny', 'comedy',
                  'entertainment', 'meme', 'cartoon', 'anime', 'gaming', 'music'
                ];
                
                const isProfessional = professionalKeywords.some(keyword => content.includes(keyword));
                const isExcluded = excludeKeywords.some(exclude => content.includes(exclude));
                
                return isProfessional && !isExcluded;
              })
              .map((article: any, idx: number) => (
                <NewsCard
                  key={article.slug || `article-${idx}`}
                  title={article.title || "AI News Article"}
                  slug={article.slug || `article-${idx}`}
                  short_summary={article.short_summary || article.description || ""}
                  source={article.source || "AI News"}
                  published_at={article.published_at}
                  thumbnail={article.thumbnail}
                  variant="vertical"
                />
              ))}
          </div>
        )}
      </main>
    </div>
  );
}
