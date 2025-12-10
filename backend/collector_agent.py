from agents.agent import Agent
from agents.run import AgentRunner
from agents.tool import function_tool
from typing import List, Dict, Optional
import re
import requests
from datetime import datetime
import os
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class CollectorAgent:
    def __init__(self):
        # Load API keys from environment
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        
        # Define methods first (without decorators)
        self._fetch_youtube_news = self._fetch_youtube_news_impl
        self._fetch_forbes_articles = self._fetch_forbes_articles_impl
        self._web_search_articles = self._web_search_articles_impl
        self._fetch_google_ai_news = self._fetch_google_ai_news_impl
        self._fetch_official_ai_sites = self._fetch_official_ai_sites_impl
        self._fetch_global_ai_news = self._fetch_global_ai_news_impl
        self._extract_source_name = self._extract_source_name
        self._clean_title = self._clean_title_impl
        self._remove_duplicates = self._remove_duplicates_impl
        
        # Note: We're using direct method calls instead of function_tool decorators
        # to avoid schema issues and ensure reliable execution
        # The Agent is defined but we use direct calls in collect_articles()
        
        # Agent definition (not actively used - we use direct method calls)
        # This is kept for potential future use with AgentRunner
        self.agent = Agent(
            name="CollectorAgent",
            instructions="""
            You are a news collector agent. Your job is to:
            1. Fetch news articles from multiple sources (YouTube, Forbes, Google AI, official AI websites, web search)
            2. Clean article titles (remove extra whitespace, special characters)
            3. Remove duplicate articles based on title similarity
            4. Return a list of unique, clean articles
            
            Always return articles in a structured format with: title, url, source, published_at
            """,
            model="gpt-4o",
            tools=[]  # Empty tools list - using direct method calls instead
        )
    
    def _fetch_youtube_news_impl(self, query: str, max_results: int = 5) -> List[Dict]:
        """Fetch YouTube news videos using YouTube Data API or RSS feed"""
        articles = []
        
        # Method 1: Use YouTube Data API if key is available
        if self.youtube_api_key:
            try:
                print(f"Using YouTube Data API to search for: '{query}'")
                api_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": f"{query} AI news latest",
                    "type": "video",
                    "maxResults": max_results,
                    "order": "date",
                    "key": self.youtube_api_key,
                    "publishedAfter": (datetime.now().replace(day=1).strftime("%Y-%m-%dT00:00:00Z"))  # This month
                }
                
                response = requests.get(api_url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    print(f"YouTube API returned {len(data.get('items', []))} videos")
                    # Professional/Technical AI keywords for filtering
                    professional_ai_keywords = [
                        'artificial intelligence', 'ai', 'machine learning', 'deep learning',
                        'neural network', 'llm', 'gpt', 'openai', 'transformer', 'nlp',
                        'computer vision', 'robotics', 'automation', 'data science',
                        'research', 'breakthrough', 'innovation', 'technology', 'algorithm',
                        'model', 'training', 'inference', 'architecture', 'neural', 'tensor',
                        'pytorch', 'tensorflow', 'dataset', 'benchmark', 'paper', 'study',
                        'conference', 'journal', 'publication', 'researcher', 'scientist',
                        'development', 'implementation', 'framework', 'library', 'api'
                    ]
                    
                    # Strict exclusion keywords for entertainment content
                    exclude_keywords = [
                        'shorts', '#shorts', 'viral', 'trending', 'fitness', 'motivation',
                        'funny', 'comedy', 'entertainment', 'meme', 'joke', 'prank',
                        'cartoon', 'anime', 'naruto', 'pokemon', 'gaming', 'game',
                        'music', 'song', 'dance', 'tiktok', 'reels', 'instagram',
                        'cooking', 'recipe', 'food', 'travel', 'vlog', 'lifestyle',
                        'beauty', 'makeup', 'fashion', 'celebrity', 'gossip'
                    ]
                    
                    for item in data.get("items", []):
                        snippet = item.get("snippet", {})
                        title = snippet.get("title", "")
                        description = snippet.get("description", "")
                        channel_title = snippet.get("channelTitle", "").lower()
                        
                        # Filter for professional/technical AI content
                        content = f"{title} {description} {channel_title}".lower()
                        is_professional_ai = any(keyword in content for keyword in professional_ai_keywords)
                        
                        # Exclude entertainment content strictly
                        has_exclude = any(exclude in content for exclude in exclude_keywords)
                        
                        # Only include professional AI content, exclude entertainment
                        if is_professional_ai and not has_exclude:
                            video_id = item.get('id', {}).get('videoId', '')
                            thumbnails = snippet.get("thumbnails", {})
                            thumbnail_url = thumbnails.get("high", {}).get("url") or thumbnails.get("medium", {}).get("url") or thumbnails.get("default", {}).get("url")
                            
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            articles.append({
                                "title": title,
                                "url": video_url,
                                "source": "youtube",
                                "published_at": snippet.get("publishedAt", datetime.now().isoformat()),
                                "description": description[:200],
                                "thumbnail": thumbnail_url,
                                "video_url": video_url,
                                "documentation_url": None
                            })
                            
                            if len(articles) >= max_results:
                                break
                    if articles:
                        print(f"Successfully fetched {len(articles)} YouTube videos")
                        return articles
                else:
                    error_data = response.json() if response.text else {}
                    print(f"YouTube API error {response.status_code}: {error_data.get('error', {}).get('message', response.text[:200])}")
            except Exception as e:
                print(f"Error using YouTube API: {e}")
                import traceback
                traceback.print_exc()
        
        # Method 2: Use RSS feeds (no API key needed)
        try:
            import feedparser
            
            # Official AI YouTube channels
            official_ai_channels = [
                "UCXZCJLdBC09EAR_GWYH9pWQ",  # OpenAI
                "UCJs2QbeTkm8G3Dg-_7V8SOQ",  # Google AI
                "UCrB7D8X3YFf3L2qJ8fX9JHg",  # DeepMind
                "UCbfYPyITQ-7l4upoX8nvctg",  # Two Minute Papers
                "UCSHZKy0bq3C3uH1n2xbt4mg",  # Lex Fridman
                "UCrB7D8X3YFf3L2qJ8fX9JHg",  # Anthropic (if available)
            ]
            
            for channel_id in ai_channels[:2]:  # Limit to avoid too many requests
                try:
                    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                    feed = feedparser.parse(rss_url)
                    
                    for entry in feed.entries[:max_results]:
                        title = entry.get('title', '')
                        # Filter for AI-related content
                        if any(term in title.lower() for term in ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt', query.lower()]):
                            articles.append({
                                "title": title,
                                "url": entry.get('link', ''),
                                "source": "youtube",
                                "published_at": entry.get('published', datetime.now().isoformat()),
                                "description": entry.get('summary', '')[:200] if hasattr(entry, 'summary') else ''
                            })
                            
                            if len(articles) >= max_results:
                                break
                    
                    if len(articles) >= max_results:
                        break
                except Exception as e:
                    print(f"Error fetching YouTube RSS for channel {channel_id}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching YouTube news: {e}")
        
        # Fallback if no results
        if not articles:
            return [{
                "title": f"YouTube: {query} - Latest AI Updates",
                "url": f"https://youtube.com/results?search_query={query.replace(' ', '+')}+AI",
                "source": "youtube",
                "published_at": datetime.now().isoformat()
            }]
        
        return articles[:max_results]
    
    def _fetch_google_ai_news_impl(self, query: str, max_results: int = 5) -> List[Dict]:
        """Fetch news from Google AI Blog and official Google AI sources"""
        articles = []
        
        try:
            import feedparser
            
            # Google AI Blog RSS
            rss_urls = [
                "https://ai.googleblog.com/feeds/posts/default",
            ]
            
            for rss_url in rss_urls:
                try:
                    feed = feedparser.parse(rss_url)
                    for entry in feed.entries[:max_results]:
                        articles.append({
                            "title": entry.get('title', ''),
                            "url": entry.get('link', ''),
                            "source": "google_ai",
                            "published_at": entry.get('published', datetime.now().isoformat()),
                            "description": entry.get('summary', '')[:200] if hasattr(entry, 'summary') else ''
                        })
                except Exception as e:
                    print(f"Error parsing Google AI RSS {rss_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching Google AI news: {e}")
        
        return articles[:max_results]
    
    def _fetch_official_ai_sites_impl(self, query: str, max_results: int = 5) -> List[Dict]:
        """Fetch news from official AI company websites"""
        articles = []
        
        try:
            import feedparser
            
            # Official AI company documentation and blog RSS feeds
            official_docs_rss = [
                "https://ai.googleblog.com/feeds/posts/default",  # Google AI Blog
                "https://openai.com/blog/rss.xml",  # OpenAI Blog (if available)
                "https://www.deepmind.com/blog/feed",  # DeepMind Blog
                "https://www.anthropic.com/news/rss.xml",  # Anthropic News
            ]
            
            # Try to fetch from official RSS feeds
            try:
                import feedparser
                for rss_url in official_docs_rss:
                    try:
                        feed = feedparser.parse(rss_url)
                        if feed.entries:
                            for entry in feed.entries[:max_results]:
                                doc_url = entry.get('link', '')
                                articles.append({
                                    "title": entry.get('title', ''),
                                    "url": doc_url,
                                    "source": "official_docs",
                                    "published_at": entry.get('published', datetime.now().isoformat()),
                                    "description": entry.get('summary', '')[:200] if hasattr(entry, 'summary') else '',
                                    "documentation_url": doc_url,
                                    "video_url": None
                                })
                                if len(articles) >= max_results:
                                    break
                        if len(articles) >= max_results:
                            break
                    except Exception as e:
                        print(f"Error parsing RSS feed {rss_url}: {e}")
                        continue
            except Exception as e:
                print(f"Error fetching official RSS feeds: {e}")
            
            # Use Google Custom Search API if available to search official sites
            if self.google_search_api_key and self.google_search_engine_id:
                try:
                    search_url = "https://www.googleapis.com/customsearch/v1"
                    params = {
                        "key": self.google_search_api_key,
                        "cx": self.google_search_engine_id,
                        "q": f"{query} site:openai.com OR site:anthropic.com OR site:deepmind.com",
                        "num": max_results
                    }
                    
                    response = requests.get(search_url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get("items", []):
                            doc_url = item.get("link", "")
                            articles.append({
                                "title": item.get("title", ""),
                                "url": doc_url,
                                "source": "official_ai",
                                "published_at": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", datetime.now().isoformat()),
                                "description": item.get("snippet", "")[:200],
                                "documentation_url": doc_url,
                                "video_url": None
                            })
                except Exception as e:
                    print(f"Error using Google Custom Search: {e}")
            
            # Use SerpAPI as alternative
            elif self.serpapi_key:
                try:
                    serpapi_url = "https://serpapi.com/search"
                    params = {
                        "api_key": self.serpapi_key,
                        "engine": "google",
                        "q": f"{query} site:openai.com OR site:anthropic.com",
                        "num": max_results
                    }
                    
                    response = requests.get(serpapi_url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        for result in data.get("organic_results", [])[:max_results]:
                            articles.append({
                                "title": result.get("title", ""),
                                "url": result.get("link", ""),
                                "source": "official_ai",
                                "published_at": result.get("date", datetime.now().isoformat()),
                                "description": result.get("snippet", "")[:200]
                            })
                except Exception as e:
                    print(f"Error using SerpAPI: {e}")
            
        except Exception as e:
            print(f"Error fetching official AI sites: {e}")
        
        return articles[:max_results]
    
    def _fetch_forbes_articles_impl(self, query: str, max_results: int = 5) -> List[Dict]:
        """Fetch recent Forbes articles using RSS feed"""
        try:
            import feedparser
            
            # Forbes RSS feeds - try multiple sources
            rss_urls = [
                "https://www.forbes.com/real-time/feed2/",
                "https://www.forbes.com/innovation/feed2/",
                "https://www.forbes.com/ai/feed2/",
            ]
            
            articles = []
            for rss_url in rss_urls:
                try:
                    feed = feedparser.parse(rss_url)
                    if feed.entries:
                        for entry in feed.entries[:max_results]:
                            # Filter for AI-related content
                            title = entry.get('title', '')
                            if 'ai' in title.lower() or 'artificial intelligence' in title.lower() or query.lower() in title.lower():
                                articles.append({
                                    "title": title,
                                    "url": entry.get('link', ''),
                                    "source": "forbes",
                                    "published_at": entry.get('published', datetime.now().isoformat())
                                })
                except Exception as e:
                    print(f"Error parsing Forbes RSS {rss_url}: {e}")
                    continue
                
                if len(articles) >= max_results:
                    break
            
            # If no RSS results, use web search fallback
            if not articles:
                # Search Forbes website for AI news
                search_query = f"{query} site:forbes.com AI"
                web_results = self._web_search_articles_impl(search_query, max_results=max_results)
                # Filter to only Forbes URLs
                for result in web_results:
                    if 'forbes.com' in result.get('url', ''):
                        result['source'] = 'forbes'
                        articles.append(result)
            
            # Fallback if still no results
            if not articles:
                articles = [
                    {
                        "title": f"Forbes: {query} - Industry Analysis",
                        "url": f"https://forbes.com/{query.replace(' ', '-')}",
                        "source": "forbes",
                        "published_at": datetime.now().isoformat()
                    }
                ]
            
            return articles[:max_results]
        except Exception as e:
            print(f"Error fetching Forbes articles: {e}")
            # Return fallback
            return [
                {
                    "title": f"Forbes: {query} - Latest News",
                    "url": f"https://forbes.com/{query.replace(' ', '-')}",
                    "source": "forbes",
                    "published_at": datetime.now().isoformat()
                }
            ]
    
    def _web_search_articles_impl(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for articles using RSS feeds from major tech news sites"""
        try:
            import feedparser
            
            # Major tech/AI news RSS feeds
            rss_feeds = [
                {
                    "url": "https://techcrunch.com/feed/",
                    "source": "techcrunch",
                    "filter": ["ai", "artificial intelligence", "machine learning", "llm", "gpt", "openai"]
                },
                {
                    "url": "https://www.theverge.com/rss/index.xml",
                    "source": "theverge",
                    "filter": ["ai", "artificial intelligence", "machine learning"]
                },
                {
                    "url": "https://feeds.feedburner.com/oreilly/radar",
                    "source": "oreilly",
                    "filter": ["ai", "artificial intelligence"]
                },
                {
                    "url": "https://www.wired.com/feed/rss",
                    "source": "wired",
                    "filter": ["ai", "artificial intelligence", "machine learning"]
                },
                {
                    "url": "https://arstechnica.com/feed/",
                    "source": "arstechnica",
                    "filter": ["ai", "artificial intelligence"]
                }
            ]
            
            articles = []
            search_terms = query.lower().split()
            
            for feed_config in rss_feeds:
                try:
                    feed = feedparser.parse(feed_config["url"])
                    if not feed.entries:
                        continue
                    
                    for entry in feed.entries[:max_results * 2]:  # Get more to filter
                        title = entry.get('title', '').lower()
                        description = entry.get('summary', '').lower() if hasattr(entry, 'summary') else ''
                        content = title + ' ' + description
                        
                        # Filter for AI-related content
                        is_relevant = any(
                            term in content or 
                            any(filt in content for filt in feed_config["filter"])
                            for term in search_terms
                        ) if search_terms else True
                        
                        if is_relevant or 'ai' in content or 'artificial intelligence' in content:
                            # Parse published date
                            published = entry.get('published', '')
                            try:
                                from dateutil import parser as date_parser
                                published_dt = date_parser.parse(published)
                                published_iso = published_dt.isoformat()
                            except:
                                published_iso = datetime.now().isoformat()
                            
                            articles.append({
                                "title": entry.get('title', 'Untitled'),
                                "url": entry.get('link', ''),
                                "source": feed_config["source"],
                                "published_at": published_iso,
                                "description": entry.get('summary', '')[:200] if hasattr(entry, 'summary') else ''
                            })
                            
                            if len(articles) >= max_results:
                                break
                    
                    if len(articles) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"Error parsing RSS feed {feed_config['url']}: {e}")
                    continue
            
            # If we still don't have enough, try additional sources
            if len(articles) < max_results:
                additional_feeds = [
                    "https://feeds.feedburner.com/venturebeat/SZYF",
                    "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
                ]
                
                for feed_url in additional_feeds:
                    try:
                        feed = feedparser.parse(feed_url)
                        for entry in feed.entries[:max_results - len(articles)]:
                            published = entry.get('published', '')
                            try:
                                from dateutil import parser as date_parser
                                published_dt = date_parser.parse(published)
                                published_iso = published_dt.isoformat()
                            except:
                                published_iso = datetime.now().isoformat()
                            
                            articles.append({
                                "title": entry.get('title', 'Untitled'),
                                "url": entry.get('link', ''),
                                "source": "tech_news",
                                "published_at": published_iso,
                                "description": entry.get('summary', '')[:200] if hasattr(entry, 'summary') else ''
                            })
                            
                            if len(articles) >= max_results:
                                break
                    except Exception as e:
                        print(f"Error with additional feed {feed_url}: {e}")
                        continue
            
            return articles[:max_results]
            
        except Exception as e:
            print(f"Error fetching web articles: {e}")
            import traceback
            traceback.print_exc()
            # Return empty list instead of fake data
            return []
    
    def _fetch_global_ai_news_impl(self, query: str, max_results: int = 10) -> List[Dict]:
        """Fetch articles from global AI news websites via RSS feeds"""
        articles = []
        
        try:
            import feedparser
            
            # Global AI news websites RSS feeds
            global_ai_sources = [
                # Tech News Sites
                "https://techcrunch.com/tag/artificial-intelligence/feed/",
                "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
                "https://www.wired.com/feed/tag/ai/latest/rss",
                "https://arstechnica.com/tag/artificial-intelligence/feed/",
                "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
                
                # Research & Academic
                "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
                "https://venturebeat.com/ai/feed/",
                "https://www.artificialintelligence-news.com/feed/",
                
                # Company Blogs
                "https://ai.googleblog.com/feeds/posts/default",
                "https://www.deepmind.com/blog/feed",
                "https://www.anthropic.com/news/rss.xml",
            ]
            
            professional_keywords = [
                'artificial intelligence', 'ai', 'machine learning', 'deep learning',
                'neural network', 'llm', 'gpt', 'openai', 'transformer', 'nlp',
                'computer vision', 'robotics', 'automation', 'data science',
                'research', 'breakthrough', 'innovation', 'technology', 'algorithm',
                'model', 'training', 'inference', 'architecture', 'neural', 'tensor',
                'pytorch', 'tensorflow', 'dataset', 'benchmark', 'paper', 'study',
                'conference', 'journal', 'publication', 'researcher', 'scientist'
            ]
            
            exclude_keywords = [
                'shorts', '#shorts', 'viral', 'trending', 'funny', 'comedy',
                'entertainment', 'meme', 'cartoon', 'anime', 'gaming', 'music',
                'cooking', 'recipe', 'food', 'travel', 'vlog', 'lifestyle'
            ]
            
            for rss_url in global_ai_sources:
                try:
                    feed = feedparser.parse(rss_url)
                    if not feed.entries:
                        continue
                    
                    for entry in feed.entries[:max_results]:
                        title = entry.get('title', '')
                        description = entry.get('summary', '') if hasattr(entry, 'summary') else ''
                        link = entry.get('link', '')
                        
                        # Filter for professional AI content
                        content = f"{title} {description}".lower()
                        is_professional = any(keyword in content for keyword in professional_keywords)
                        has_exclude = any(exclude in content for exclude in exclude_keywords)
                        
                        if is_professional and not has_exclude:
                            # Parse published date
                            published_iso = datetime.now().isoformat()
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                try:
                                    from time import mktime
                                    published_iso = datetime.fromtimestamp(mktime(entry.published_parsed)).isoformat()
                                except:
                                    pass
                            
                            articles.append({
                                "title": title,
                                "url": link,
                                "source": self._extract_source_name(rss_url),
                                "published_at": published_iso,
                                "description": description[:500] if description else ""
                            })
                            
                            if len(articles) >= max_results * 2:  # Collect more for deduplication
                                break
                    
                    if len(articles) >= max_results * 2:
                        break
                except Exception as e:
                    print(f"Error fetching RSS feed {rss_url}: {e}")
                    continue
            
            return articles[:max_results]
        except Exception as e:
            print(f"Error fetching global AI news: {e}")
            return []
    
    def _extract_source_name(self, url: str) -> str:
        """Extract source name from RSS URL"""
        if 'techcrunch' in url:
            return 'techcrunch'
        elif 'theverge' in url:
            return 'the_verge'
        elif 'wired' in url:
            return 'wired'
        elif 'arstechnica' in url:
            return 'ars_technica'
        elif 'zdnet' in url:
            return 'zdnet'
        elif 'technologyreview' in url or 'mit' in url:
            return 'mit_tech_review'
        elif 'venturebeat' in url:
            return 'venturebeat'
        elif 'artificialintelligence-news' in url:
            return 'ai_news'
        elif 'googleblog' in url:
            return 'google_ai'
        elif 'deepmind' in url:
            return 'deepmind'
        elif 'anthropic' in url:
            return 'anthropic'
        else:
            return 'ai_news'
    
    def _clean_title_impl(self, title: str) -> str:
        """Clean article title: remove extra whitespace, normalize characters"""
        if not title:
            return ""
        
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Remove special characters at start/end
        title = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', title)
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
        
        return title
    
    def _remove_duplicates_impl(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL and title similarity"""
        if not articles:
            return []
        
        seen_urls = set()
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            url = article.get("url", "").strip()
            title = article.get("title", "").lower().strip()
            
            # Skip if URL already seen (exact duplicate)
            if url and url in seen_urls:
                continue
            
            # Skip if title is empty
            if not title:
                continue
            
            # Check for similar titles (fuzzy matching)
            is_duplicate = False
            for seen_title in seen_titles:
                # Normalize titles for comparison
                title_normalized = re.sub(r'[^\w\s]', '', title)
                seen_normalized = re.sub(r'[^\w\s]', '', seen_title)
                
                # Check exact match
                if title_normalized == seen_normalized:
                    is_duplicate = True
                    break
                
                # Check word overlap similarity
                title_words = set(title_normalized.split())
                seen_words = set(seen_normalized.split())
                
                if len(title_words) > 0 and len(seen_words) > 0:
                    # Calculate Jaccard similarity
                    intersection = len(title_words & seen_words)
                    union = len(title_words | seen_words)
                    similarity = intersection / union if union > 0 else 0
                    
                    # If >80% similar, consider duplicate
                    if similarity > 0.8:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                if url:
                    seen_urls.add(url)
                seen_titles.add(title)
                unique_articles.append(article)
        
        print(f"Deduplication: {len(articles)} articles -> {len(unique_articles)} unique articles")
        return unique_articles
    
    async def collect_articles(self, topic: Optional[str] = None, max_articles: int = 10) -> List[Dict]:
        """Main method to collect articles from all sources"""
        search_query = topic or "AI news latest"
        
        print(f"Collecting articles with query: '{search_query}', max: {max_articles}")
        print(f"YouTube API Key: {'Set' if self.youtube_api_key else 'Not set'}")
        print(f"Google Search API Key: {'Set' if self.google_search_api_key else 'Not set'}")
        print(f"Google Search Engine ID: {'Set' if self.google_search_engine_id else 'Not set'}")
        
        # Collect from all sources in parallel (using direct calls for reliability)
        youtube_articles = self._fetch_youtube_news_impl(search_query, max_results=max_articles)
        print(f"YouTube: Found {len(youtube_articles)} articles")
        
        google_ai_articles = self._fetch_google_ai_news_impl(search_query, max_results=max_articles)
        print(f"Google AI: Found {len(google_ai_articles)} articles")
        
        official_ai_articles = self._fetch_official_ai_sites_impl(search_query, max_results=max_articles)
        print(f"Official AI Sites: Found {len(official_ai_articles)} articles")
        
        # NEW: Fetch from global AI news sources
        global_ai_articles = self._fetch_global_ai_news_impl(search_query, max_results=max_articles * 2)
        print(f"Global AI News: Found {len(global_ai_articles)} articles")
        
        forbes_articles = self._fetch_forbes_articles_impl(search_query, max_results=max_articles)
        print(f"Forbes: Found {len(forbes_articles)} articles")
        
        web_articles = self._web_search_articles_impl(search_query, max_results=max_articles)
        print(f"Web Search: Found {len(web_articles)} articles")
        
        # Combine all articles
        all_articles = youtube_articles + google_ai_articles + official_ai_articles + global_ai_articles + forbes_articles + web_articles
        print(f"Total articles collected from all sources: {len(all_articles)}")
        
        # Clean titles
        for article in all_articles:
            article["title"] = self._clean_title_impl(article.get("title", ""))
        
        # Remove duplicates
        unique_articles = self._remove_duplicates_impl(all_articles)
        print(f"Unique articles after deduplication: {len(unique_articles)}")
        
        # Filter for professional/technical AI content only
        professional_ai_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
            'neural network', 'llm', 'large language model', 'gpt', 'openai',
            'transformer', 'nlp', 'natural language processing', 'computer vision',
            'robotics', 'automation', 'data science', 'algorithm', 'model',
            'research', 'paper', 'study', 'breakthrough', 'innovation',
            'technology', 'tech', 'development', 'advancement', 'progress',
            'training', 'inference', 'architecture', 'neural', 'tensor',
            'pytorch', 'tensorflow', 'dataset', 'benchmark', 'conference',
            'journal', 'publication', 'researcher', 'scientist', 'framework'
        ]
        
        # Strict exclusion for entertainment content
        exclude_keywords = [
            'shorts', '#shorts', 'viral', 'trending', 'fitness', 'motivation',
            'funny', 'comedy', 'entertainment', 'meme', 'joke', 'prank',
            'cartoon', 'anime', 'naruto', 'pokemon', 'gaming', 'game',
            'music', 'song', 'dance', 'tiktok', 'reels', 'instagram',
            'cooking', 'recipe', 'food', 'travel', 'vlog', 'lifestyle',
            'beauty', 'makeup', 'fashion', 'celebrity', 'gossip'
        ]
        
        filtered_articles = []
        for article in unique_articles:
            title = (article.get("title", "") or "").lower()
            description = (article.get("description", "") or "").lower()
            source = (article.get("source", "") or "").lower()
            
            # Check if article is professional AI/knowledge related
            content = f"{title} {description} {source}"
            is_professional_ai = any(keyword in content for keyword in professional_ai_keywords)
            
            # Exclude entertainment content strictly
            has_exclude = any(exclude in content for exclude in exclude_keywords)
            
            # Only include if professional AI-related AND not excluded
            if is_professional_ai and not has_exclude:
                filtered_articles.append(article)
        
        print(f"AI-filtered articles: {len(filtered_articles)} (from {len(unique_articles)} unique)")
        
        # Limit to max_articles
        final_articles = filtered_articles[:max_articles]
        print(f"Returning {len(final_articles)} AI-focused articles")
        
        return final_articles
