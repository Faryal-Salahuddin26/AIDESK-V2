import Link from "next/link";
import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Calendar, Sparkles, ExternalLink, Clock } from "lucide-react";

interface NewsCardProps {
  title: string;
  slug: string;
  short_summary: string;
  source: string;
  published_at?: string;
  thumbnail?: string;
  variant?: "vertical" | "horizontal";
}

export function NewsCard({
  title,
  slug,
  short_summary,
  source,
  published_at,
  thumbnail,
  variant = "vertical",
}: NewsCardProps) {
  const formattedDate = published_at
    ? new Date(published_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : null;

  const timeAgo = published_at
    ? (() => {
        const now = new Date();
        const published = new Date(published_at);
        const diffInSeconds = Math.floor((now.getTime() - published.getTime()) / 1000);
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        const diffInHours = Math.floor(diffInMinutes / 60);
        const diffInDays = Math.floor(diffInHours / 24);
        
        if (diffInMinutes < 1) return "Just now";
        if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
        if (diffInHours < 24) return `${diffInHours}h ago`;
        if (diffInDays < 7) return `${diffInDays}d ago`;
        return formattedDate;
      })()
    : null;

  if (variant === "horizontal") {
    return (
      <Link href={`/news/${slug}`}>
        <Card className="group overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-primary/5 border border-border/50 bg-card hover:-translate-y-0.5 hover:border-primary/30 w-full">
          <CardContent className="p-0">
            <div className="flex flex-col sm:flex-row gap-4 sm:gap-5 p-4 sm:p-5 lg:p-6 items-start">
              {thumbnail ? (
                <div className="relative w-full sm:w-28 md:w-32 lg:w-36 h-48 sm:h-28 md:h-32 lg:h-36 flex-shrink-0 rounded-xl overflow-hidden bg-gradient-to-br from-primary/10 to-purple-500/10 border border-border/50 shadow-sm">
                  <Image
                    src={thumbnail}
                    alt={title}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-110"
                    sizes="(max-width: 640px) 100vw, (max-width: 768px) 112px, (max-width: 1024px) 128px, 144px"
                  />
                </div>
              ) : (
                <div className="relative w-full sm:w-28 md:w-32 lg:w-36 h-48 sm:h-28 md:h-32 lg:h-36 flex-shrink-0 rounded-xl overflow-hidden bg-gradient-to-br from-primary/20 via-purple-500/20 to-pink-500/20 border border-border/50 flex items-center justify-center">
                  <div className="relative">
                    <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse pointer-events-none"></div>
                    <Sparkles className="h-8 w-8 sm:h-10 sm:w-10 text-primary relative z-10" />
                  </div>
                </div>
              )}
              <div className="flex-1 py-0 sm:py-1 space-y-2 sm:space-y-3 min-w-0 flex flex-col w-full sm:w-auto">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="inline-flex items-center px-2.5 sm:px-3 py-1 text-xs font-semibold bg-primary/10 text-primary rounded-full border border-primary/20 whitespace-nowrap">
                    {source}
                  </span>
                  {timeAgo && (
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground whitespace-nowrap">
                      <Clock className="h-3 w-3 flex-shrink-0" />
                      <time dateTime={published_at}>{timeAgo}</time>
                    </div>
                  )}
                </div>
                <h2 className="text-base sm:text-lg md:text-xl font-bold leading-tight line-clamp-2 group-hover:text-primary transition-colors break-words">
                  {title}
                </h2>
                {short_summary && (
                  <p className="text-sm text-muted-foreground line-clamp-2 sm:line-clamp-2 leading-relaxed break-words">
                    {short_summary}
                  </p>
                )}
                <div className="flex items-center gap-2 text-xs text-primary font-medium opacity-0 group-hover:opacity-100 transition-opacity mt-auto pt-1">
                  <span>Read article</span>
                  <ExternalLink className="h-3 w-3 flex-shrink-0" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </Link>
    );
  }

  return (
    <Link href={`/news/${slug}`}>
      <Card className="group h-full overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 border border-border/50 hover:border-primary/30 bg-card">
        {thumbnail ? (
          <div className="relative h-48 w-full overflow-hidden bg-gradient-to-br from-primary/10 to-purple-500/10">
            <Image
              src={thumbnail}
              alt={title}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-110"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          </div>
        ) : (
          <div className="relative h-48 w-full overflow-hidden bg-gradient-to-br from-primary/20 via-purple-500/20 to-pink-500/20 flex items-center justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-2xl rounded-full animate-pulse"></div>
              <Sparkles className="h-16 w-16 text-primary relative z-10" />
            </div>
          </div>
        )}
        <CardContent className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20">
              {source}
            </span>
            {formattedDate && (
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Calendar className="h-3.5 w-3.5" />
                <time dateTime={published_at}>{formattedDate}</time>
              </div>
            )}
          </div>
          <h2 className="text-xl font-bold leading-tight line-clamp-2 group-hover:text-primary transition-colors">
            {title}
          </h2>
          <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">
            {short_summary}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
