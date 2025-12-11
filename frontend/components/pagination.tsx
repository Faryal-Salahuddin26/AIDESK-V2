import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  baseUrl?: string;
  className?: string;
}

export function Pagination({ currentPage, totalPages, baseUrl = "/", className }: PaginationProps) {
  if (totalPages <= 1) return null;

  const getPageUrl = (page: number) => {
    if (page === 1) return baseUrl;
    return `${baseUrl}?page=${page}`;
  };

  const pages = [];
  const maxVisible = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  return (
    <nav aria-label="Pagination" className={cn("flex items-center justify-center gap-2", className)}>
      <Link href={getPageUrl(currentPage - 1)}>
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage === 1}
          className="h-9"
        >
          <ChevronLeft className="h-4 w-4" />
          <span className="sr-only">Previous page</span>
        </Button>
      </Link>

      {startPage > 1 && (
        <>
          <Link href={getPageUrl(1)}>
            <Button variant="outline" size="sm" className="h-9">
              1
            </Button>
          </Link>
          {startPage > 2 && <span className="px-2 text-muted-foreground">...</span>}
        </>
      )}

      {pages.map((page) => (
        <Link key={page} href={getPageUrl(page)}>
          <Button
            variant={currentPage === page ? "default" : "outline"}
            size="sm"
            className="h-9 min-w-[36px]"
          >
            {page}
          </Button>
        </Link>
      ))}

      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span className="px-2 text-muted-foreground">...</span>}
          <Link href={getPageUrl(totalPages)}>
            <Button variant="outline" size="sm" className="h-9">
              {totalPages}
            </Button>
          </Link>
        </>
      )}

      <Link href={getPageUrl(currentPage + 1)}>
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage === totalPages}
          className="h-9"
        >
          <ChevronRight className="h-4 w-4" />
          <span className="sr-only">Next page</span>
        </Button>
      </Link>
    </nav>
  );
}

