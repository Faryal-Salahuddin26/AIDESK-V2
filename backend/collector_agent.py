"""
Collector Agent - Fetches articles from multiple sources and normalizes them.
Sources: YouTube (transcripts/posts), Forbes, Web Search (Bing/Google)
"""
from agents.agent import Agent
from agents.run import AgentRunner
from typing import List, Dict, Optional, Any
import re
import requests
from datetime import datetime
import os
from urllib.parse import urlparse, urljoin
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import feedparser
except ImportError:
    feedparser = None


class CollectorAgent:
    """Collects articles from YouTube, Forbes, and web search, normalizing all results."""
    
    def __init__(self):
        # Load API keys from environment
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.bing_search_api_key = os.getenv("BING_SEARCH_API_KEY")
        self.google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Agent for content extraction fallback
        self.agent = Agent(
            name="CollectorAgent",
            instructions="""
            You are a news collector agent. Your job is to:
            1. Fetch articles from YouTube (transcripts/posts), Forbes, and web search
            2. Normalize all results to a consistent structure
            3. Extract content from web pages when needed
            4. Return normalized articles with: title, url, content, published_at, thumbnail
            """,
            model="gpt-4o",
            tools=[]
        )
    
    def normalize_article(self, raw_article: Dict[str, Any]) -> Dict[str, str]:
        """
        Normalize article to standard structure:
        {
            "title": string,
            "url": string,
            "content": string,
            "published_at": ISO string,
            "thumbnail": string
        }
        Also preserves additional fields like "source", "description" for compatibility.
        """
        # Extract and normalize fields
        title = str(raw_article.get("title", "")).strip()
        url = str(raw_article.get("url", "")).strip()
        
        # Get content from various possible fields
        content = (
            raw_article.get("content") or
            raw_article.get("description") or
            raw_article.get("summary") or
            raw_article.get("snippet") or
            ""
        )
        content = str(content).strip()
        
        # Normalize published_at to ISO format
        published_at = raw_article.get("published_at") or raw_article.get("published") or raw_article.get("date")
        if published_at:
            try:
                if isinstance(published_at, str):
                    # Try parsing various date formats
                    from dateutil import parser as date_parser
                    published_dt = date_parser.parse(published_at)
                    published_at = published_dt.isoformat()
                elif hasattr(published_at, 'isoformat'):
                    published_at = published_at.isoformat()
            except:
                published_at = datetime.now().isoformat()
        else:
            published_at = datetime.now().isoformat()
        
        # Get thumbnail from various possible fields
        thumbnail = (
            raw_article.get("thumbnail") or
            raw_article.get("thumbnail_url") or
            raw_article.get("image") or
            raw_article.get("image_url") or
            ""
        )
        thumbnail = str(thumbnail).strip()
        
        # If thumbnail is relative URL, make it absolute
        if thumbnail and not thumbnail.startswith(('http://', 'https://')):
            if url:
                thumbnail = urljoin(url, thumbnail)
        
        # Build normalized article (required fields)
        normalized = {
            "title": title,
            "url": url,
            "content": content,
            "published_at": published_at,
            "thumbnail": thumbnail
        }
        
        # Preserve additional fields for compatibility
        normalized["source"] = raw_article.get("source", "unknown")
        if "description" in raw_article and raw_article["description"] != content:
            normalized["description"] = raw_article["description"]
        elif not normalized.get("description") and content:
            # Use content as description if description not provided
            normalized["description"] = content[:500]
        if "video_url" in raw_article:
            normalized["video_url"] = raw_article["video_url"]
        if "documentation_url" in raw_article:
            normalized["documentation_url"] = raw_article["documentation_url"]
        
        return normalized
    
    def fetch_youtube_articles(self, query: str = "AI news latest", max_results: int = 10) -> List[Dict[str, str]]:
        """
        Fetch YouTube videos/transcripts using YouTube Data API or RSS feeds.
        Returns normalized articles.
        """
        articles = []
        
        # Method 1: YouTube Data API
        if self.youtube_api_key:
            try:
                print(f"Fetching YouTube videos via API for: '{query}'")
                api_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": f"{query} AI",
                    "type": "video",
                    "maxResults": max_results,
                    "order": "date",
                    "key": self.youtube_api_key,
                    "publishedAfter": (datetime.now().replace(day=1).strftime("%Y-%m-%dT00:00:00Z"))
                }
                
                response = requests.get(api_url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("items", []):
                        snippet = item.get("snippet", {})
                        video_id = item.get("id", {}).get("videoId", "")
                        
                        # Get video details for transcript
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        description = snippet.get("description", "")
                        
                        # Try to get transcript (YouTube doesn't provide API for this, but we can note it)
                        # For now, use description as content
                        content = description or snippet.get("title", "")
                        
                        thumbnails = snippet.get("thumbnails", {})
                        thumbnail = (
                            thumbnails.get("high", {}).get("url") or
                            thumbnails.get("medium", {}).get("url") or
                            thumbnails.get("default", {}).get("url") or
                            ""
                        )
                        
                        raw_article = {
                            "title": snippet.get("title", ""),
                            "url": video_url,
                            "content": content,
                            "description": description[:500] if description else "",
                            "published_at": snippet.get("publishedAt", ""),
                            "thumbnail": thumbnail,
                            "source": "youtube",
                            "video_id": video_id,
                            "video_url": video_url
                        }
                        
                        articles.append(self.normalize_article(raw_article))
                        
                        if len(articles) >= max_results:
                            break
                    
                    if articles:
                        print(f"Fetched {len(articles)} YouTube videos via API")
                        return articles
            except Exception as e:
                print(f"Error using YouTube API: {e}")
        
        # Method 2: RSS Feeds (fallback)
        if feedparser:
            try:
                print("Trying YouTube RSS feeds...")
                # Popular AI YouTube channels
                channel_ids = [
                    "UCXZCJLdBC09EAR_GWYH9pWQ",  # OpenAI
                    "UCJs2QbeTkm8G3Dg-_7V8SOQ",  # Google AI
                ]
                
                for channel_id in channel_ids[:2]:  # Limit to avoid too many requests
                    try:
                        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                        feed = feedparser.parse(rss_url)
                        
                        for entry in feed.entries[:max_results]:
                            summary = entry.get("summary", "") if hasattr(entry, "summary") else ""
                            raw_article = {
                                "title": entry.get("title", ""),
                                "url": entry.get("link", ""),
                                "content": summary,
                                "description": summary[:500] if summary else "",
                                "published_at": entry.get("published", ""),
                                "thumbnail": "",  # RSS doesn't provide thumbnails
                                "source": "youtube",
                                "video_url": entry.get("link", "")
                            }
                            
                            articles.append(self.normalize_article(raw_article))
                            
                            if len(articles) >= max_results:
                                break
                        
                        if len(articles) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error fetching YouTube RSS for channel {channel_id}: {e}")
                        continue
            except Exception as e:
                print(f"Error fetching YouTube RSS: {e}")
        
        print(f"Fetched {len(articles)} YouTube articles")
        return articles[:max_results]
    
    def fetch_forbes_articles(self, query: str = "AI business", max_results: int = 10) -> List[Dict[str, str]]:
        """
        Fetch Forbes articles using RSS feeds or HTML scraping.
        Returns normalized articles.
        """
        articles = []
        
        # Method 1: RSS Feeds
        if feedparser:
            try:
                print(f"Fetching Forbes articles via RSS for: '{query}'")
                rss_urls = [
                    "https://www.forbes.com/real-time/feed2/",
                    "https://www.forbes.com/innovation/feed2/",
                    "https://www.forbes.com/ai/feed2/",
                ]
                
                for rss_url in rss_urls:
                    try:
                        feed = feedparser.parse(rss_url)
                        if not feed.entries:
                            continue
                        
                        for entry in feed.entries[:max_results]:
                            title = entry.get("title", "")
                            # Filter for AI-related content
                            if query.lower() in title.lower() or "ai" in title.lower() or "artificial intelligence" in title.lower():
                                summary = entry.get("summary", "") if hasattr(entry, "summary") else ""
                                raw_article = {
                                    "title": title,
                                    "url": entry.get("link", ""),
                                    "content": summary,
                                    "description": summary[:500] if summary else "",
                                    "published_at": entry.get("published", ""),
                                    "thumbnail": "",
                                    "source": "forbes"
                                }
                                
                                articles.append(self.normalize_article(raw_article))
                                
                                if len(articles) >= max_results:
                                    break
                        
                        if len(articles) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error parsing Forbes RSS {rss_url}: {e}")
                        continue
            except Exception as e:
                print(f"Error fetching Forbes RSS: {e}")
        
        # Method 2: HTML Scraping (fallback if RSS fails)
        if len(articles) < max_results:
            try:
                print("Trying Forbes HTML scraping...")
                forbes_urls = [
                    "https://www.forbes.com/innovation/",
                    "https://www.forbes.com/ai/",
                ]
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                for url in forbes_urls:
                    try:
                        response = requests.get(url, headers=headers, timeout=10)
                        if response.status_code == 200 and BeautifulSoup:
                            soup = BeautifulSoup(response.content, "html.parser")
                            
                            # Find article links
                            article_links = soup.find_all("a", href=re.compile(r"/\d{4}/\d{2}/\d{2}/"))
                            
                            for link in article_links[:max_results]:
                                article_url = urljoin("https://www.forbes.com", link.get("href", ""))
                                title = link.get_text(strip=True)
                                
                                if title and query.lower() in title.lower():
                                    raw_article = {
                                        "title": title,
                                        "url": article_url,
                                        "content": "",  # Will be fetched later if needed
                                        "description": "",
                                        "published_at": datetime.now().isoformat(),
                                        "thumbnail": "",
                                        "source": "forbes"
                                    }
                                    
                                    articles.append(self.normalize_article(raw_article))
                                    
                                    if len(articles) >= max_results:
                                        break
                        
                        if len(articles) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error scraping Forbes {url}: {e}")
                        continue
            except Exception as e:
                print(f"Error scraping Forbes: {e}")
        
        print(f"Fetched {len(articles)} Forbes articles")
        return articles[:max_results]
    
    def fetch_web_search_articles(self, query: str = "AI news", max_results: int = 10) -> List[Dict[str, str]]:
        """
        Fetch articles from web search using Bing Search API or Google Custom Search.
        Returns normalized articles.
        """
        articles = []
        
        # Method 1: Bing Search API (preferred)
        if self.bing_search_api_key:
            try:
                print(f"Fetching web articles via Bing Search API for: '{query}'")
                api_url = "https://api.bing.microsoft.com/v7.0/search"
                headers = {
                    "Ocp-Apim-Subscription-Key": self.bing_search_api_key
                }
                params = {
                    "q": f"{query} AI news",
                    "count": max_results,
                    "offset": 0,
                    "mkt": "en-US",
                    "safeSearch": "Moderate"
                }
                
                response = requests.get(api_url, headers=headers, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("webPages", {}).get("value", []):
                        snippet = item.get("snippet", "")
                        raw_article = {
                            "title": item.get("name", ""),
                            "url": item.get("url", ""),
                            "content": snippet,
                            "description": snippet[:500] if snippet else "",
                            "published_at": item.get("datePublished", datetime.now().isoformat()),
                            "thumbnail": "",
                            "source": "web_search"
                        }
                        
                        articles.append(self.normalize_article(raw_article))
                    
                    if articles:
                        print(f"Fetched {len(articles)} articles via Bing Search API")
                        return articles
            except Exception as e:
                print(f"Error using Bing Search API: {e}")
        
        # Method 2: Google Custom Search API (fallback)
        if self.google_search_api_key and self.google_search_engine_id:
            try:
                print(f"Fetching web articles via Google Custom Search for: '{query}'")
                api_url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.google_search_api_key,
                    "cx": self.google_search_engine_id,
                    "q": f"{query} AI news",
                    "num": max_results
                }
                
                response = requests.get(api_url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("items", []):
                        snippet = item.get("snippet", "")
                        raw_article = {
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "content": snippet,
                            "description": snippet[:500] if snippet else "",
                            "published_at": datetime.now().isoformat(),
                            "thumbnail": "",
                            "source": "web_search"
                        }
                        
                        articles.append(self.normalize_article(raw_article))
                    
                    if articles:
                        print(f"Fetched {len(articles)} articles via Google Custom Search")
                        return articles
            except Exception as e:
                print(f"Error using Google Custom Search: {e}")
        
        # Method 3: RSS Feeds (fallback)
        if feedparser and len(articles) < max_results:
            try:
                print("Trying RSS feeds as fallback...")
                rss_feeds = [
                    {"url": "https://techcrunch.com/feed/", "source": "techcrunch"},
                    {"url": "https://www.theverge.com/rss/index.xml", "source": "theverge"},
                    {"url": "https://www.wired.com/feed/rss", "source": "wired"},
                ]
                
                for feed_config in rss_feeds:
                    try:
                        feed = feedparser.parse(feed_config["url"])
                        if not feed.entries:
                            continue
                        
                        for entry in feed.entries[:max_results]:
                            title = entry.get("title", "")
                            if query.lower() in title.lower() or "ai" in title.lower():
                                summary = entry.get("summary", "") if hasattr(entry, "summary") else ""
                                raw_article = {
                                    "title": title,
                                    "url": entry.get("link", ""),
                                    "content": summary,
                                    "description": summary[:500] if summary else "",
                                    "published_at": entry.get("published", ""),
                                    "thumbnail": "",
                                    "source": feed_config["source"]
                                }
                                
                                articles.append(self.normalize_article(raw_article))
                                
                                if len(articles) >= max_results:
                                    break
                        
                        if len(articles) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error parsing RSS feed {feed_config['url']}: {e}")
                        continue
            except Exception as e:
                print(f"Error fetching RSS feeds: {e}")
        
        print(f"Fetched {len(articles)} web search articles")
        return articles[:max_results]
    
    def extract_content_with_fallback(self, article: Dict[str, str]) -> Dict[str, str]:
        """
        Fallback: If content not available, fetch webpage and extract content.
        Uses ArticleFetcher service if available, otherwise uses simple scraping.
        """
        # If content already exists and is substantial, return as-is
        if article.get("content") and len(article["content"]) > 200:
            return article
        
        url = article.get("url", "")
        if not url:
            return article
        
        print(f"Extracting content from: {url}")
        
        try:
            # Try using ArticleFetcher service
            try:
                from app.services.article_fetcher import ArticleFetcher
                fetcher = ArticleFetcher()
                result = fetcher.fetch_article_content(url, article.get("title", ""), article.get("content", ""))
                
                if result.get("content") and len(result["content"]) > 200:
                    article["content"] = result["content"]
                    if result.get("thumbnail") and not article.get("thumbnail"):
                        article["thumbnail"] = result.get("thumbnail", "")
                    print(f"Successfully extracted {len(result['content'])} characters from {url}")
                    return article
            except ImportError:
                print("ArticleFetcher not available, using simple scraping...")
            except Exception as e:
                print(f"Error using ArticleFetcher: {e}")
            
            # Fallback: Simple HTML scraping
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200 and BeautifulSoup:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Remove unwanted elements
                for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    tag.decompose()
                
                # Try to find main content
                main_content = (
                    soup.find("article") or
                    soup.find("main") or
                    soup.find(class_=re.compile("article|content|post", re.I)) or
                    soup
                )
                
                # Extract text
                content = main_content.get_text(separator="\n\n", strip=True)
                # Clean up excessive whitespace
                content = re.sub(r"\n{3,}", "\n\n", content)
                
                if len(content) > 200:
                    article["content"] = content[:5000]  # Limit to 5000 chars
                    print(f"Extracted {len(content)} characters via simple scraping")
                    
                    # Try to get thumbnail
                    img = soup.find("img")
                    if img and img.get("src"):
                        article["thumbnail"] = urljoin(url, img["src"])
                    
                    return article
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
        
        # If all fails, return article as-is (with minimal content)
        return article
    
    async def collect_articles(self, topic: Optional[str] = None, max_articles: int = 20) -> List[Dict[str, str]]:
        """
        Main method to collect articles from all sources.
        Returns normalized articles with consistent structure.
        """
        query = topic or "AI news latest"
        
        print(f"\n{'='*60}")
        print(f"Collecting articles: '{query}' (max: {max_articles})")
        print(f"{'='*60}")
        print(f"YouTube API Key: {'✓ Set' if self.youtube_api_key else '✗ Not set'}")
        print(f"Bing Search API Key: {'✓ Set' if self.bing_search_api_key else '✗ Not set'}")
        print(f"Google Search API Key: {'✓ Set' if self.google_search_api_key else '✗ Not set'}")
        print(f"{'='*60}\n")
        
        all_articles = []
        
        # Fetch from all sources
        youtube_articles = self.fetch_youtube_articles(query, max_results=max_articles // 3)
        print(f"✓ YouTube: {len(youtube_articles)} articles\n")
        all_articles.extend(youtube_articles)
        
        forbes_articles = self.fetch_forbes_articles(query, max_results=max_articles // 3)
        print(f"✓ Forbes: {len(forbes_articles)} articles\n")
        all_articles.extend(forbes_articles)
        
        web_articles = self.fetch_web_search_articles(query, max_results=max_articles // 3)
        print(f"✓ Web Search: {len(web_articles)} articles\n")
        all_articles.extend(web_articles)
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        print(f"Total unique articles: {len(unique_articles)}")
        
        # Extract content for articles missing content (fallback)
        print("\nExtracting content for articles missing content...")
        for article in unique_articles:
            if not article.get("content") or len(article.get("content", "")) < 200:
                article = self.extract_content_with_fallback(article)
        
        # Limit to max_articles
        final_articles = unique_articles[:max_articles]
        
        print(f"\n{'='*60}")
        print(f"Final result: {len(final_articles)} normalized articles")
        print(f"{'='*60}\n")
        
        return final_articles
