import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SummaryCardProps {
  title: string;
  short_summary: string;
  long_summary: string;
}

export function SummaryCard({
  title,
  short_summary,
  long_summary,
}: SummaryCardProps) {
  return (
    <Card className="border-border/50 bg-card">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl sm:text-2xl">Article Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {short_summary && (
          <div>
            <h3 className="text-sm font-semibold mb-3 text-foreground uppercase tracking-wide">Quick Summary</h3>
            <p className="text-base sm:text-lg leading-relaxed text-muted-foreground break-words">
              {short_summary}
            </p>
          </div>
        )}
        {long_summary && long_summary !== short_summary && (
          <div>
            <h3 className="text-sm font-semibold mb-3 text-foreground uppercase tracking-wide">Detailed Summary</h3>
            <p className="text-base sm:text-lg leading-relaxed text-muted-foreground whitespace-pre-wrap break-words">
              {long_summary}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

