"""
perplexity_connector.py
---------------------------------------------------------
Purpose:
    Lightweight connector that allows any management-layer
    agent to query Perplexity AI for up-to-date research.

Key Features:
    • Simple search(query) function
    • Optional focus modes (research / news / code)
    • Returns summary text, sources, and metadata
    • Compatible with Planning Agent pipeline

Setup:
    1. Obtain your Perplexity API key:
         https://www.perplexity.ai/settings/api
    2. Store it in config/.env:
         PERPLEXITY_API_KEY="pplx-your-key"
---------------------------------------------------------
"""

import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Use central config loader
from src.utils.config_loader import load_env, get_env

# Ensure environment is loaded
load_env()

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
DEFAULT_MODEL = "sonar-pro"  # Pro model with web access


class PerplexityConnector:
    """
    Connector for Perplexity AI research queries.
    
    Automatically loads API key from config/.env
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        """
        Initialize Perplexity connector.
        
        Args:
            api_key: Perplexity API key (or from config/.env)
            model: Model name (default: sonar-pro)
        """
        self.api_key = api_key or get_env("PERPLEXITY_API_KEY")
        if not self.api_key or "your-" in self.api_key:
            raise ValueError(
                "Missing PERPLEXITY_API_KEY. "
                "Please set it in config/.env file. "
                "Get your key at: https://www.perplexity.ai/settings/api"
            )
        
        self.model = model

    def search(self, query: str, focus: str = "research") -> Dict[str, Any]:
        """
        Send a search query to Perplexity.
        
        Args:
            query: Research question
            focus: Context (research/news/code)
            
        Returns:
            Dict with summary, sources, metadata
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                PERPLEXITY_API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract content
            output_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = data.get("citations", [])
            created_at = datetime.utcnow().isoformat()
            
            return {
                "query": query,
                "summary": output_text,
                "sources": citations,
                "timestamp": created_at,
                "model": self.model,
                "focus": focus
            }
            
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = response.json()
            except:
                error_detail = response.text
            raise Exception(f"Perplexity API error: {e}\nDetails: {error_detail}")

    @staticmethod
    def format_markdown(result: Dict[str, Any]) -> str:
        """Format result as markdown."""
        lines = [
            f"### 🔍 Research Query: {result['query']}",
            f"**Model:** {result['model']}",
            f"**Timestamp:** {result['timestamp']} UTC\n",
            f"{result['summary']}\n",
        ]
        if result.get("sources"):
            lines.append("**Sources:**")
            for s in result["sources"]:
                lines.append(f"- {s}")
        return "\n".join(lines)


if __name__ == "__main__":
    """Test the connector"""
    print("\n" + "=" * 70)
    print("🔍 PERPLEXITY CONNECTOR TEST")
    print("=" * 70 + "\n")
    
    try:
        connector = PerplexityConnector()
        topic = "latest agile milestone planning frameworks for AI software projects"
        
        print(f"📡 Querying: {topic}")
        print("⏳ Wait...\n")
        
        result = connector.search(topic)
        
        print("=" * 70)
        print("📘 RESULT")
        print("=" * 70 + "\n")
        print(PerplexityConnector.format_markdown(result))
        print("\n" + "=" * 70)
        print("✅ SUCCESS")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
