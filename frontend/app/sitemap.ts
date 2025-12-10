import { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://aidesk.com';
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  try {
    // Get all articles
    const response = await fetch(
      `${apiUrl}/api/v1/list-news?page=1&limit=1000`,
      { 
        next: { revalidate: 3600 },
        cache: 'force-cache',
      }
    );
    
    if (!response.ok) {
      // Return just homepage if backend is unavailable
      return [
        {
          url: baseUrl,
          lastModified: new Date(),
          changeFrequency: 'hourly',
          priority: 1,
        },
      ];
    }
    
    const data = await response.json();
    const articles = data.articles || [];
    
    // Generate sitemap entries
    const articleEntries: MetadataRoute.Sitemap = articles.map((article: any) => ({
      url: `${baseUrl}/news/${article.slug}`,
      lastModified: article.published_at ? new Date(article.published_at) : new Date(),
      changeFrequency: 'hourly',
      priority: 0.8,
    }));
    
    return [
      {
        url: baseUrl,
        lastModified: new Date(),
        changeFrequency: 'hourly',
        priority: 1,
      },
      ...articleEntries,
    ];
  } catch (error) {
    console.error('Error generating sitemap:', error);
    return [
      {
        url: baseUrl,
        lastModified: new Date(),
        changeFrequency: 'hourly',
        priority: 1,
      },
    ];
  }
}

