"""Service to fetch full article content from URLs."""
import requests
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

class ArticleFetcher:
    """Fetch and parse COMPLETE article content from URLs - extracts ALL original content."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract main article content using multiple strategies."""
        # Strategy 1: Look for semantic HTML5 article tags
        article = soup.find('article')
        if article:
            return article
        
        # Strategy 2: Look for common content containers
        content_selectors = [
            '[role="article"]',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.article-body',
            '.post-body',
            '.content-body',
            '.main-content',
            '.article-text',
            '.post-text',
            '#article-body',
            '#content',
            '#main-content',
            'main article',
            'main .content',
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Check if it has substantial content
                text_length = len(element.get_text(strip=True))
                if text_length > 200:  # At least 200 characters
                    return element
        
        # Strategy 3: Find container with most paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            # Group paragraphs by parent
            parent_groups = {}
            for p in paragraphs:
                parent = p.find_parent(['article', 'div', 'section', 'main'])
                if parent:
                    parent_id = id(parent)
                    if parent_id not in parent_groups:
                        parent_groups[parent_id] = {
                            'element': parent,
                            'paragraphs': [],
                            'text_length': 0
                        }
                    parent_groups[parent_id]['paragraphs'].append(p)
                    parent_groups[parent_id]['text_length'] += len(p.get_text(strip=True))
            
            # Find parent with most content
            if parent_groups:
                best_parent = max(parent_groups.values(), key=lambda x: x['text_length'])
                if best_parent['text_length'] > 500:  # At least 500 characters
                    return best_parent['element']
        
        # Strategy 4: Find main content area
        main = soup.find('main')
        if main:
            text_length = len(main.get_text(strip=True))
            if text_length > 300:
                return main
        
        return None
    
    def _clean_content(self, element: BeautifulSoup) -> BeautifulSoup:
        """Remove unwanted elements from content."""
        # Remove unwanted tags
        unwanted_tags = [
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            'advertisement', 'ad', 'ads', '.ad', '.ads', '.advertisement',
            '.social-share', '.share-buttons', '.newsletter', '.subscribe',
            '.comments', '#comments', '.related-posts', '.related-articles',
            '.sidebar', '#sidebar', '.menu', '.navigation', '.breadcrumb',
            '.author-box', '.author-info', '.tags', '.categories',
        ]
        
        for tag in unwanted_tags:
            try:
                for element_to_remove in element.select(tag):
                    element_to_remove.decompose()
            except:
                pass
        
        # Remove elements with common ad/related class names
        unwanted_classes = ['ad', 'ads', 'advertisement', 'promo', 'sponsored', 
                           'related', 'sidebar', 'social-share', 'newsletter']
        for class_name in unwanted_classes:
            try:
                for element_to_remove in element.find_all(class_=re.compile(class_name, re.I)):
                    element_to_remove.decompose()
            except:
                pass
        
        return element
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract and convert image URLs to absolute URLs."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                # Convert to absolute URL
                absolute_url = urljoin(base_url, src)
                images.append({
                    'url': absolute_url,
                    'alt': img.get('alt', '')
                })
        return images
    
    def fetch_article_content(self, url: str, title: str = "", description: str = "") -> Dict[str, str]:
        """
        Fetch COMPLETE article content from URL - extracts ALL content from original source.
        Returns dict with 'content' (full text), 'html_content' (formatted HTML), and 'images'.
        """
        try:
            # Skip YouTube URLs - they're videos, not articles
            if 'youtube.com' in url or 'youtu.be' in url:
                return {
                    "content": description or title or "",
                    "html_content": None,
                    "is_video": True,
                    "images": []
                }
            
            print(f"Fetching full content from: {url}")
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main content using multiple strategies
            main_content = self._extract_main_content(soup)
            
            if main_content:
                # Clean unwanted elements
                main_content = self._clean_content(main_content)
                
                # Extract all text content (including headings, lists, etc.)
                # Get all text elements in order
                text_elements = []
                
                # Extract headings
                for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    text = heading.get_text(strip=True)
                    if text:
                        level = heading.name
                        text_elements.append(f"{'#' * int(level[1])} {text}\n")
                
                # Extract paragraphs
                for p in main_content.find_all('p'):
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Skip very short paragraphs (likely ads)
                        text_elements.append(text)
                
                # Extract lists
                for ul in main_content.find_all(['ul', 'ol']):
                    list_items = []
                    for li in ul.find_all('li', recursive=False):
                        item_text = li.get_text(strip=True)
                        if item_text:
                            list_items.append(f"• {item_text}")
                    if list_items:
                        text_elements.append('\n'.join(list_items))
                
                # Extract blockquotes
                for blockquote in main_content.find_all('blockquote'):
                    quote_text = blockquote.get_text(strip=True)
                    if quote_text:
                        text_elements.append(f"> {quote_text}")
                
                # Combine all text
                full_text_content = '\n\n'.join(text_elements)
                
                # If we didn't get much text, try getting all text from main_content
                if len(full_text_content) < 500:
                    full_text_content = main_content.get_text(separator='\n\n', strip=True)
                    # Clean up excessive whitespace
                    full_text_content = re.sub(r'\n{3,}', '\n\n', full_text_content)
                
                # Get HTML content (preserve structure)
                html_content = str(main_content)
                
                # Clean HTML more thoroughly
                html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                html_content = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                
                # Extract images
                images = self._extract_images(main_content, url)
                
                # Extract links for reference
                links = []
                for a in main_content.find_all('a', href=True):
                    link_text = a.get_text(strip=True)
                    link_url = urljoin(url, a['href'])
                    if link_text and link_url:
                        links.append({
                            'text': link_text,
                            'url': link_url
                        })
                
                return {
                    "content": full_text_content or description or title or "",
                    "html_content": html_content,
                    "is_video": False,
                    "images": images[:10],  # Limit to 10 images
                    "links": links[:20],  # Limit to 20 links
                    "source_url": url,
                    "content_length": len(full_text_content)
                }
            else:
                # Fallback: extract all meaningful content
                # Remove unwanted elements first
                for unwanted in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    unwanted.decompose()
                
                # Get all text
                text_content = soup.get_text(separator='\n\n', strip=True)
                # Clean up excessive whitespace
                text_content = re.sub(r'\n{3,}', '\n\n', text_content)
                # Remove very short lines (likely navigation/ads)
                lines = text_content.split('\n\n')
                meaningful_lines = [line for line in lines if len(line.strip()) > 30]
                text_content = '\n\n'.join(meaningful_lines)
                
                return {
                    "content": text_content[:10000] or description or title or "",  # Increased limit
                    "html_content": None,
                    "is_video": False,
                    "images": [],
                    "links": [],
                    "source_url": url,
                    "content_length": len(text_content)
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching article from {url}: {e}")
            return {
                "content": description or title or "",
                "html_content": None,
                "is_video": False,
                "error": str(e)
            }
        except Exception as e:
            print(f"Error parsing article from {url}: {e}")
            return {
                "content": description or title or "",
                "html_content": None,
                "is_video": False,
                "error": str(e)
            }

