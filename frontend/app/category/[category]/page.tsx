import { NewsCard } from "@/components/NewsCard";
import { NewsList } from "@/components/NewsList";
import { notFound } from "next/navigation";
import { 
  Wrench, 
  Microscope, 
  Building2, 
  Rocket, 
  Bot, 
  Lightbulb,
  Sparkles 
} from "lucide-react";
import type { Metadata } from "next";

// Revalidate every 5 minutes
export const revalidate = 300;

// Category definitions with icons and metadata
const CATEGORIES = {
  "ai-tools": {
    name: "AI Tools",
    icon: Wrench,
    color: "text-yellow-500",
    bgColor: "bg-yellow-500/10",
    description: "Discover the latest AI tools, platforms, and software revolutionizing how we work.",
    keywords: ["tools", "software", "platform", "application", "utility", "product"],
  },
  "research": {
    name: "Research",
    icon: Microscope,
    color: "text-white",
    bgColor: "bg-white/10",
    description: "Cutting-edge AI research papers, breakthroughs, and scientific discoveries.",
    keywords: ["research", "paper", "study", "academic", "scientific", "publication"],
  },
  "industry": {
    name: "Industry",
    icon: Building2,
    color: "text-blue-400",
    bgColor: "bg-blue-500/10",
    description: "AI industry news, enterprise adoption, and business insights.",
    keywords: ["industry", "enterprise", "business", "corporate", "commercial", "market"],
  },
  "startups": {
    name: "Startups",
    icon: Rocket,
    color: "text-red-500",
    bgColor: "bg-red-500/10",
    description: "AI startups, funding rounds, and innovative new companies.",
    keywords: ["startup", "funding", "venture", "unicorn", "founder", "company"],
  },
  "models": {
    name: "Models",
    icon: Bot,
    color: "text-gray-400",
    bgColor: "bg-gray-500/10",
    description: "New AI models, architectures, and model releases from leading labs.",
    keywords: ["model", "llm", "gpt", "architecture", "neural", "training"],
  },
  "breakthroughs": {
    name: "Breakthroughs",
    icon: Lightbulb,
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/10",
    description: "Major AI breakthroughs, milestones, and game-changing innovations.",
    keywords: ["breakthrough", "milestone", "innovation", "discovery", "achievement", "advance"],
  },
} as const;

type CategorySlug = keyof typeof CATEGORIES;

async function getArticles(categorySlug: string) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  try {
    const response = await fetch(
      `${apiUrl}/list-news?page=1&limit=50`,
      {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        cache: 'no-store',
      }
    );
    
    if (!response.ok) {
      console.error(`❌ API Error: ${response.status} ${response.statusText}`);
      return [];
    }
    
    const data = await response.json();
    const articles = Array.isArray(data) 
      ? data 
      : (data.articles || []);
    
    return filterArticlesByCategory(articles, categorySlug);
  } catch (error) {
    console.error("Error fetching articles:", error);
    return [];
  }
}

function filterArticlesByCategory(articles: any[], categorySlug: string): any[] {
  const category = CATEGORIES[categorySlug as CategorySlug];
  if (!category) return articles;
  
  // Filter articles by tags or title/content keywords
  return articles.filter((article) => {
    const title = (article.title || "").toLowerCase();
    const tags = (article.tags || []).map((tag: string) => tag.toLowerCase());
    const summary = (article.short_summary || article.description || "").toLowerCase();
    const source = (article.source || "").toLowerCase();
    
    // Check if any category keyword matches
    const matchesKeyword = category.keywords.some((keyword) => {
      return (
        title.includes(keyword) ||
        summary.includes(keyword) ||
        tags.includes(keyword) ||
        source.includes(keyword)
      );
    });
    
    // Also check tags for category name
    const matchesCategoryName = tags.some((tag: string) => 
      tag.includes(category.name.toLowerCase()) ||
      category.name.toLowerCase().includes(tag)
    );
    
    return matchesKeyword || matchesCategoryName;
  });
}

export async function generateMetadata({ 
  params 
}: { 
  params: Promise<{ category: string }> 
}): Promise<Metadata> {
  const { category: categoryParam } = await params;
  const categorySlug = categoryParam as CategorySlug;
  const category = CATEGORIES[categorySlug];
  
  if (!category) {
    return {
      title: "Category Not Found",
    };
  }
  
  return {
    title: `${category.name} | AI DESK`,
    description: category.description,
    keywords: [...category.keywords, "AI", "Artificial Intelligence", category.name],
  };
}

export default async function CategoryPage({ 
  params 
}: { 
  params: Promise<{ category: string }> 
}) {
  const { category: categoryParam } = await params;
  const categorySlug = categoryParam as CategorySlug;
  const category = CATEGORIES[categorySlug];
  
  if (!category) {
    notFound();
  }
  
  const articles = await getArticles(categorySlug);
  const Icon = category.icon;
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
          {/* Hero Section */}
          <div className="border-b border-border/50 bg-gradient-to-b from-muted/30 to-background">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-12 sm:py-14 lg:py-16">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6 mb-4 sm:mb-6 animate-fade-in">
            <div className={`p-4 rounded-2xl ${category.bgColor} border ${category.color.includes('yellow') ? 'border-yellow-500/20' : category.color.includes('white') ? 'border-white/20' : category.color.includes('blue') ? 'border-blue-500/20' : category.color.includes('red') ? 'border-red-500/20' : category.color.includes('gray') ? 'border-gray-500/20' : 'border-primary/20'} shadow-lg`}>
              <Icon className="h-10 w-10" />
            </div>
            <div className="flex-1">
              <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-3">
                {category.name}
              </h1>
              <p className="text-muted-foreground text-lg leading-relaxed">
                {category.description}
              </p>
            </div>
          </div>
          
          {/* Category Stats */}
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2 px-4 py-2 bg-card/80 backdrop-blur-sm rounded-full border border-border/50 shadow-sm">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="font-semibold">{articles.length} {articles.length === 1 ? 'article' : 'articles'}</span>
            </div>
          </div>
        </div>
      </div>
      
          {/* Articles Section */}
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-8 sm:py-10 lg:py-12">
        {articles.length === 0 ? (
          <div className="py-20 text-center animate-fade-in">
            <div className="space-y-6 max-w-md mx-auto">
              <div className={`p-6 rounded-2xl ${category.bgColor} inline-block border ${category.color.includes('yellow') ? 'border-yellow-500/20' : category.color.includes('white') ? 'border-white/20' : category.color.includes('blue') ? 'border-blue-500/20' : category.color.includes('red') ? 'border-red-500/20' : category.color.includes('gray') ? 'border-gray-500/20' : 'border-primary/20'}`}>
                <Icon className={`h-16 w-16 ${category.color} mx-auto`} />
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-2">No articles yet</h3>
                <p className="text-muted-foreground mb-4">
                  Articles in this category will appear here once they are collected.
                </p>
                <p className="text-xs text-muted-foreground">
                  News is collected automatically every 15 minutes
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {articles.map((article: any) => (
              <NewsCard
                key={article.slug || article.title}
                title={article.title}
                slug={article.slug}
                short_summary={article.short_summary || article.description}
                source={article.source}
                published_at={article.published_at}
                thumbnail={article.thumbnail}
                variant="horizontal"
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Generate static params for all categories
export async function generateStaticParams() {
  return Object.keys(CATEGORIES).map((category) => ({
    category,
  }));
}

