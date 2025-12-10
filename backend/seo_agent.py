from agents.agent import Agent
from agents.run import AgentRunner
from agents.tool import function_tool
from typing import Dict, List
import re
import unicodedata


class SEOAgent:
    def __init__(self):
        # Wrap methods with function_tool
        self.generate_slug = function_tool(self._generate_slug_impl)
        self.extract_tags = function_tool(self._extract_tags_impl)
        
        self.agent = Agent(
            name="SEOAgent",
            instructions="""
            You are an SEO optimization agent. Your job is to generate:
            1. meta_title: SEO-optimized title (50-60 characters)
            2. meta_description: SEO-optimized description (150-160 characters)
            3. slug: URL-friendly slug from title
            4. tags: Relevant tags/keywords (5-10 tags)
            
            All outputs should be optimized for search engines and user engagement.
            """,
            model="gpt-4o",
            tools=[
                self.generate_slug,
                self.extract_tags
            ]
        )
    
    def _generate_slug_impl(self, title: str) -> str:
        """Generate a URL-friendly slug from a title"""
        if not title:
            return ""
        
        # Convert to lowercase
        slug = title.lower()
        
        # Remove special characters, keep only alphanumeric and spaces
        slug = re.sub(r'[^\w\s-]', '', slug)
        
        # Replace spaces with hyphens
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 100:
            slug = slug[:100]
        
        return slug
    
    def _extract_tags_impl(self, title: str, content: str) -> List[str]:
        """Extract relevant tags/keywords from title and content"""
        # Common AI-related tags
        ai_tags = [
            "artificial intelligence", "machine learning", "AI", "ML", 
            "deep learning", "neural networks", "automation", "technology",
            "innovation", "tech news", "AI news", "future tech"
        ]
        
        # Extract keywords from title
        title_lower = title.lower()
        tags = []
        
        for tag in ai_tags:
            if tag.lower() in title_lower or tag.lower() in content.lower():
                tags.append(tag)
        
        # Add topic-specific tags based on keywords
        keywords = ["openai", "chatgpt", "gpt", "llm", "generative", "robotics", 
                   "computer vision", "nlp", "natural language", "transformer"]
        
        for keyword in keywords:
            if keyword in title_lower or keyword in content.lower():
                tags.append(keyword)
        
        # Ensure we have at least 5 tags, max 10
        if len(tags) < 5:
            tags.extend(ai_tags[:5-len(tags)])
        
        return tags[:10]
    
    async def generate_seo(self, title: str, content: str) -> Dict:
        """Generate all SEO metadata for an article"""
        prompt = f"""
        Generate SEO metadata for this article:
        
        Title: {title}
        Content preview: {content[:500]}...
        
        Generate:
        1. meta_title: SEO-optimized title (50-60 characters, include main keywords)
        2. meta_description: SEO-optimized description (150-160 characters, compelling and keyword-rich)
        3. slug: URL-friendly slug (use generate_slug function)
        4. tags: Relevant tags (use extract_tags function, 5-10 tags)
        
        Return a JSON object with:
        {{
            "meta_title": "...",
            "meta_description": "...",
            "slug": "...",
            "tags": ["tag1", "tag2", ...]
        }}
        """
        
        # Use OpenAI API directly to generate SEO metadata
        from openai import OpenAI
        import os
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        try:
            # Generate SEO metadata using OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an SEO expert. Generate optimized metadata for search engines."
                    },
                    {
                        "role": "user",
                        "content": f"""Generate SEO metadata for this article:

Title: {title}
Content preview: {content[:500]}...

Generate:
1. meta_title: SEO-optimized title (50-60 characters, include main keywords)
2. meta_description: SEO-optimized description (150-160 characters, compelling and keyword-rich)
3. slug: URL-friendly slug (lowercase, hyphens, no special chars)
4. tags: Relevant tags (5-10 tags, JSON array)

Return ONLY a JSON object with:
{{
    "meta_title": "...",
    "meta_description": "...",
    "slug": "...",
    "tags": ["tag1", "tag2", ...]
}}"""
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Ensure slug is properly formatted
            slug = result.get("slug", self._generate_slug_impl(title))
            if not slug:
                slug = self._generate_slug_impl(title)
            
            # Ensure tags are valid
            tags = result.get("tags", [])
            if not tags or len(tags) < 5:
                tags = self._extract_tags_impl(title, content)
            
            return {
                "meta_title": result.get("meta_title", title[:60]),
                "meta_description": result.get("meta_description", content[:160] if content else ""),
                "slug": slug,
                "tags": tags[:10]
            }
        except Exception as e:
            print(f"Error using OpenAI API for SEO: {e}")
            # Fallback to direct method calls
            slug = self._generate_slug_impl(title)
            meta_title = title[:60] if len(title) <= 60 else title[:57] + "..."
            meta_description = (content[:160] if content else title)[:160]
            tags = self._extract_tags_impl(title, content)
            
            return {
                "meta_title": meta_title,
                "meta_description": meta_description,
                "slug": slug,
                "tags": tags
            }
