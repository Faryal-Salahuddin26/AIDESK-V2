const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Note: Backend endpoints don't use /api/v1 prefix
// All endpoints are directly under the root path

export const api = {
  async collectNews(topic?: string, maxArticles: number = 10) {
    const response = await fetch(`${API_URL}/collect-news`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, max_articles: maxArticles }),
    });
    return response.json();
  },

  async generateSummaries(articles: any[]) {
    const response = await fetch(`${API_URL}/summaries`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ articles }),
    });
    return response.json();
  },

  async generateSEO(title: string, content: string) {
    const response = await fetch(`${API_URL}/seo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content }),
    });
    return response.json();
  },

  async saveNews(article: any) {
    const response = await fetch(`${API_URL}/save-news`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ article }),
    });
    return response.json();
  },

  async listNews(page: number = 1, limit: number = 20) {
    const response = await fetch(
      `${API_URL}/list-news?page=${page}&limit=${limit}`
    );
    return response.json();
  },

  async getNewsBySlug(slug: string) {
    const response = await fetch(`${API_URL}/news/${slug}`);
    if (!response.ok) return null;
    return response.json();
  },
};

