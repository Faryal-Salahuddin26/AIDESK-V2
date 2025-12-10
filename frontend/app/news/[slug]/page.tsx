import { notFound } from "next/navigation";
import { SummaryCard } from "@/components/SummaryCard";
import { Calendar, Tag, Youtube, BookOpen, ExternalLink } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Metadata } from "next";
import Image from "next/image";

// Revalidate every hour
export const revalidate = 3600;

// Generate static params at build time
export async function generateStaticParams() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  try {
    // Try primary endpoint with /api/v1 prefix
    let response = await fetch(
      `${apiUrl}/api/v1/list-news?page=1&limit=100`,
      { next: { revalidate: 3600 } }
    );
    
    // If 404, try endpoint without /api/v1 prefix
    if (!response.ok && response.status === 404) {
      response = await fetch(
        `${apiUrl}/list-news?page=1&limit=100`,
        { next: { revalidate: 3600 } }
      );
    }
    
    if (!response.ok) {
      return [];
    }
    
    const data = await response.json();
    const articles = Array.isArray(data) ? data : (data.articles || []);
    return articles.map((article: any) => ({
      slug: article.slug,
    }));
  } catch (error) {
    console.error("Error generating static params:", error);
    return [];
  }
}

// Generate metadata for SEO
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://aidesk.com";
  
  try {
    // Try primary endpoint with /api/v1 prefix
    let response = await fetch(
      `${apiUrl}/api/v1/news/${slug}`,
      { 
        next: { revalidate: 3600 },
        cache: 'force-cache',
      }
    );
    
    // If 404, try endpoint without /api/v1 prefix
    if (!response.ok && response.status === 404) {
      response = await fetch(
        `${apiUrl}/news/${slug}`,
        { 
          next: { revalidate: 3600 },
          cache: 'force-cache',
        }
      );
    }
    
    if (!response.ok) {
      return {
        title: "Article Not Found",
      };
    }
    
    const article = await response.json();
    
    return {
      title: article.meta_title || article.title,
      description: article.meta_description || article.short_summary,
      keywords: article.tags?.join(", "),
      openGraph: {
        title: article.meta_title || article.title,
        description: article.meta_description || article.short_summary,
        type: "article",
        url: `${siteUrl}/news/${article.slug}`,
        images: article.thumbnail ? [article.thumbnail] : [],
        publishedTime: article.published_at,
        tags: article.tags,
      },
      twitter: {
        card: "summary_large_image",
        title: article.meta_title || article.title,
        description: article.meta_description || article.short_summary,
        images: article.thumbnail ? [article.thumbnail] : [],
      },
    };
  } catch (error) {
    return {
      title: "Article Not Found",
    };
  }
}

async function getArticle(slug: string, fetchContent: boolean = true) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  try {
    // Try primary endpoint with /api/v1 prefix
    let response = await fetch(
      `${apiUrl}/api/v1/news/${slug}?fetch_content=${fetchContent}`,
      { 
        cache: 'no-store',
      }
    );
    
    // If 404, try endpoint without /api/v1 prefix (actual backend endpoint)
    if (!response.ok && response.status === 404) {
      console.log(`⚠️ /api/v1/news/${slug} not found, trying /news/${slug}...`);
      response = await fetch(
        `${apiUrl}/news/${slug}?fetch_content=${fetchContent}`,
        { 
          cache: 'no-store',
        }
      );
    }
    
    if (!response.ok) {
      console.error(`❌ Article fetch failed: ${response.status} ${response.statusText}`);
      console.error(`Tried: ${apiUrl}/api/v1/news/${slug} and ${apiUrl}/news/${slug}`);
      return null;
    }
    
    const article = await response.json();
    console.log(`✅ Article fetched successfully: ${article.title}`);
    if (article.content_fetched) {
      console.log(`✅ Full content fetched: ${article.full_content?.length || 0} characters`);
    }
    return article;
  } catch (error: any) {
    console.error("❌ Error fetching article:", error.message);
    console.error("Slug:", slug);
    console.error("API URL:", apiUrl);
    return null;
  }
}

export default async function NewsArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  // Fetch article with full content
  const article = await getArticle(slug, true);
  
  if (!article) {
    notFound();
  }

  const publishedDate = article.published_at
    ? new Date(article.published_at)
    : null;
  const formattedDate = publishedDate
    ? publishedDate.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/20">
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl py-6 sm:py-8 lg:py-12">
        <article className="space-y-4 sm:space-y-6">
          {/* Article Header */}
          <header className="mb-6 sm:mb-8 space-y-4 sm:space-y-6">
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20">
                {article.source}
              </span>
              {formattedDate && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <time dateTime={article.published_at}>{formattedDate}</time>
                </div>
              )}
            </div>

            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight tracking-tight break-words">
              {article.title}
            </h1>

            {article.tags && article.tags.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 pt-2 sm:pt-3">
                <Tag className="h-4 w-4 text-muted-foreground" />
                {article.tags.map((tag: string) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium bg-muted hover:bg-muted/80 text-muted-foreground border border-border/50"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </header>

          {/* Article Thumbnail */}
          {article.thumbnail && (
            <div className="relative w-full h-64 sm:h-80 lg:h-96 rounded-xl overflow-hidden border border-border/50 mb-6 sm:mb-8 bg-gradient-to-br from-primary/10 to-purple-500/10">
              <Image
                src={article.thumbnail}
                alt={article.title}
                fill
                className="object-cover"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 768px, 1200px"
                priority
              />
            </div>
          )}

          {/* Summary Card */}
          {(article.short_summary || article.long_summary || article.description) && (
            <SummaryCard
              title={article.title}
              short_summary={article.short_summary || article.description || ""}
              long_summary={article.long_summary || article.short_summary || article.description || ""}
            />
          )}

          {/* Full Article Content - Complete Original Content */}
          {article.full_content && article.full_content.length > 0 && !article.is_video && (
            <div className="pt-4 sm:pt-6 border-t border-border">
              <div className="flex items-center justify-between mb-4 sm:mb-6">
                <h2 className="text-xl sm:text-2xl font-bold">Complete Article</h2>
                {article.content_length && (
                  <span className="text-xs text-muted-foreground">
                    {article.content_length.toLocaleString()} characters
                  </span>
                )}
              </div>
              
              <div className="prose prose-sm sm:prose-base lg:prose-lg dark:prose-invert max-w-none">
                {article.html_content ? (
                  <div 
                    className="article-content text-base sm:text-lg leading-relaxed text-foreground"
                    dangerouslySetInnerHTML={{ __html: article.html_content }}
                  />
                ) : (
                  <div className="text-base sm:text-lg leading-relaxed text-foreground break-words">
                    {article.full_content.split('\n\n').map((paragraph: string, idx: number) => {
                      const trimmed = paragraph.trim();
                      if (!trimmed) return null;
                      
                      // Check if it's a heading (starts with #)
                      if (trimmed.startsWith('#')) {
                        const level = trimmed.match(/^#+/)?.[0]?.length || 1;
                        const headingText = trimmed.replace(/^#+\s*/, '');
                        type HeadingLevel = "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
                        const HeadingTag = `h${Math.min(level, 6)}` as HeadingLevel;
                        return (
                          <HeadingTag 
                            key={idx} 
                            className={`font-bold mb-4 mt-6 first:mt-0 ${
                              level === 1 ? 'text-3xl' : 
                              level === 2 ? 'text-2xl' : 
                              level === 3 ? 'text-xl' : 
                              'text-lg'
                            }`}
                          >
                            {headingText}
                          </HeadingTag>
                        );
                      }
                      
                      // Check if it's a blockquote (starts with >)
                      if (trimmed.startsWith('>')) {
                        return (
                          <blockquote 
                            key={idx} 
                            className="border-l-4 border-primary pl-4 my-4 italic text-muted-foreground"
                          >
                            {trimmed.replace(/^>\s*/, '')}
                          </blockquote>
                        );
                      }
                      
                      // Check if it's a list item (starts with •)
                      if (trimmed.startsWith('•')) {
                        return (
                          <li key={idx} className="ml-6 mb-2 list-disc">
                            {trimmed.replace(/^•\s*/, '')}
                          </li>
                        );
                      }
                      
                      // Regular paragraph
                      return (
                        <p key={idx} className="mb-4 last:mb-0 leading-relaxed">
                          {trimmed}
                        </p>
                      );
                    })}
                  </div>
                )}
              </div>
              
              {/* Images from article */}
              {article.images && article.images.length > 0 && (
                <div className="mt-8 pt-6 border-t border-border">
                  <h3 className="text-lg font-semibold mb-4">Article Images</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {article.images.map((img: any, idx: number) => (
                      <div key={idx} className="relative aspect-video rounded-lg overflow-hidden border border-border/50">
                        <img
                          src={img.url}
                          alt={img.alt || `Image ${idx + 1}`}
                          className="w-full h-full object-cover"
                          loading="lazy"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Related Links from article */}
              {article.links && article.links.length > 0 && (
                <div className="mt-8 pt-6 border-t border-border">
                  <h3 className="text-lg font-semibold mb-4">Related Links</h3>
                  <div className="space-y-2">
                    {article.links.map((link: any, idx: number) => (
                      <a
                        key={idx}
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 rounded-lg border border-border/50 bg-card hover:bg-muted/50 transition-all hover:border-primary/50 group"
                      >
                        <div className="flex items-center gap-2">
                          <ExternalLink className="h-4 w-4 text-primary flex-shrink-0" />
                          <span className="text-sm font-medium group-hover:text-primary transition-colors break-all">
                            {link.text}
                          </span>
                        </div>
                        <span className="text-xs text-muted-foreground mt-1 block truncate">
                          {link.url}
                        </span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Source Attribution */}
              {article.source_url && (
                <div className="mt-8 pt-6 border-t border-border">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">
                        This content was fetched from the original source
                      </p>
                      <a
                        href={article.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border border-border bg-card hover:bg-muted/50 transition-all hover:border-primary/50 hover:shadow-md"
                      >
                        <ExternalLink className="h-4 w-4 text-primary" />
                        <span className="text-sm font-medium">View Original Source</span>
                      </a>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Fallback: Show long summary if full content not available */}
          {!article.full_content && article.long_summary && (
            <div className="pt-4 sm:pt-6 border-t border-border">
              <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">Article Summary</h2>
              <div className="prose prose-sm sm:prose-base lg:prose-lg dark:prose-invert max-w-none">
                <div className="text-base sm:text-lg leading-relaxed text-foreground whitespace-pre-wrap break-words">
                  {article.long_summary}
                </div>
              </div>
              {article.url && (
                <div className="mt-6 pt-6 border-t border-border">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border border-border bg-card hover:bg-muted/50 transition-all hover:border-primary/50 hover:shadow-md"
                  >
                    <ExternalLink className="h-4 w-4 text-primary" />
                    <span className="text-sm font-medium">Read Original Article</span>
                  </a>
                </div>
              )}
            </div>
          )}

          {/* Embedded YouTube Video */}
          {article.video_url && (() => {
            // Extract YouTube video ID from URL
            const getYouTubeVideoId = (url: string): string | null => {
              const patterns = [
                /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
                /youtube\.com\/watch\?.*v=([^&\n?#]+)/
              ];
              for (const pattern of patterns) {
                const match = url.match(pattern);
                if (match && match[1]) return match[1];
              }
              return null;
            };
            
            const videoId = getYouTubeVideoId(article.video_url);
            
            return videoId ? (
              <div className="pt-4 sm:pt-6 border-t border-border">
                <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">Watch Video</h2>
                <div className="relative w-full aspect-video rounded-xl overflow-hidden border border-border/50 bg-gradient-to-br from-primary/10 to-purple-500/10">
                  <iframe
                    src={`https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1`}
                    title={article.title}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="absolute inset-0 w-full h-full"
                  />
                </div>
                {article.video_url && (
                  <div className="mt-4">
                    <a
                      href={article.video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      <span>Watch on YouTube</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                )}
              </div>
            ) : null;
          })()}

          {/* Documentation Links */}
          {article.documentation_url && (
            <div className="space-y-4 sm:space-y-6 pt-4 sm:pt-6 border-t border-border">
              <h2 className="text-xl sm:text-2xl font-bold">Related Resources</h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

                {article.documentation_url && (
                  <a
                    href={article.documentation_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 p-4 sm:p-5 lg:p-6 rounded-lg sm:rounded-xl border border-border bg-card hover:bg-muted/50 transition-all hover:shadow-lg hover:border-primary/50"
                  >
                    <div className="flex-shrink-0 p-2 sm:p-3 bg-blue-500/10 rounded-lg group-hover:bg-blue-500/20 transition-colors">
                      <BookOpen className="h-5 w-5 sm:h-6 sm:w-6 text-blue-500" />
                    </div>
                    <div className="flex-1 min-w-0 w-full sm:w-auto">
                      <h3 className="font-semibold text-base sm:text-lg mb-1 group-hover:text-primary transition-colors break-words">
                        Official Documentation
                      </h3>
                      <p className="text-sm text-muted-foreground line-clamp-2 break-words">
                        Read the official documentation
                      </p>
                      <div className="flex items-center gap-1 mt-2 text-xs text-primary">
                        <span>View Documentation</span>
                        <ExternalLink className="h-3 w-3 flex-shrink-0" />
                      </div>
                    </div>
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Back Button */}
          <div className="pt-8">
            <Link href="/">
              <Button variant="outline">
                ← Back to Home
              </Button>
            </Link>
          </div>
        </article>
      </main>
    </div>
  );
}

