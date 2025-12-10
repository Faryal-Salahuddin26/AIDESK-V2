from agents.agent import Agent
from agents.run import AgentRunner
from agents.tool import function_tool
from typing import Dict


class SummaryAgent:
    def __init__(self):
        # Wrap methods with function_tool
        self.generate_short_summary = function_tool(self._generate_short_summary_impl)
        self.generate_long_summary = function_tool(self._generate_long_summary_impl)
        
        self.agent = Agent(
            name="SummaryAgent",
            instructions="""
            You are a summarization agent. Your job is to create two types of summaries:
            1. Short summary: 100-150 characters (concise, punchy)
            2. Long summary: 500-1200 words (comprehensive, detailed)
            
            Both summaries should be engaging, informative, and well-written.
            """,
            model="gpt-4o",
            tools=[
                self.generate_short_summary,
                self.generate_long_summary
            ]
        )
    
    def _generate_short_summary_impl(self, title: str, content: str) -> str:
        """Generate a short summary of 100-150 characters"""
        # This is a helper function, actual generation happens in agent
        return ""
    
    def _generate_long_summary_impl(self, title: str, content: str) -> str:
        """Generate a long summary of 500-1200 words"""
        # This is a helper function, actual generation happens in agent
        return ""
    
    async def summarize_article(self, article: Dict) -> Dict[str, str]:
        """Generate both short and long summaries for an article or video"""
        title = article.get("title", "")
        url = article.get("url", "")
        description = article.get("description", "")
        source = article.get("source", "").lower()
        video_url = article.get("video_url", "")
        
        # Check if it's a YouTube video
        is_video = source == "youtube" or "youtube.com" in url.lower() or "youtu.be" in url.lower() or "youtube.com" in str(video_url).lower()
        
        # Use OpenAI API directly to generate summaries
        from openai import OpenAI
        import os
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        try:
            # Build content for summarization
            content_parts = [f"Title: {title}"]
            if description:
                content_parts.append(f"{'Video Description' if is_video else 'Description'}: {description}")
            content_parts.append(f"URL: {url or video_url}")
            
            content_text = "\n".join(content_parts)
            
            # Generate summaries using OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional {'video' if is_video else 'news'} summarizer. Generate concise and engaging summaries."
                    },
                    {
                        "role": "user",
                        "content": f"""Create summaries for this {'video' if is_video else 'article'}:

{content_text}

Generate:
1. A short summary (100-150 characters) - concise and punchy, highlighting key points
2. A long summary (500-1200 words) - comprehensive and detailed, covering all important aspects

{'For videos: Focus on the main topics discussed, key insights, technical details, and important takeaways.' if is_video else 'For articles: Focus on the main arguments, findings, implications, and key information.'}

Return ONLY a JSON object with:
{{
    "short_summary": "...",
    "long_summary": "..."
}}"""
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                "short_summary": result.get("short_summary", "")[:200],
                "long_summary": result.get("long_summary", "")
            }
        except Exception as e:
            print(f"Error using OpenAI API: {e}")
            # Fallback to simple summaries
            short_summary = f"{title}. Latest AI developments and insights."[:150]
            long_summary = f"{title}. This article covers the latest developments in artificial intelligence, exploring recent breakthroughs, industry trends, and technological innovations in the AI space."
            return {
                "short_summary": short_summary,
                "long_summary": long_summary
            }
