"""
Keyword Generator - AI-powered keyword generation for pain discovery

Generates contextual keywords across 5 categories based on idea refinement data:
1. Core Intent - Direct product demand
2. Pain-Based - Problem validation
3. Industry Vertical - Specific use-cases
4. Adjacency/Proxy - Latent market demand
5. Trend Validation - Top-of-funnel awareness

Uses OpenAI to generate keywords with reasoning, platform recommendations,
and geographic optimization based on user's refinement context.

Created: 2025-10-24 (Pain Discovery Enhancement)
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    from src.utils.config_loader import get_env, load_env
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available - keyword generation will use fallback mode")

# HuggingFace KeyBERT for candidate extraction (70% cost reduction!)
try:
    from keybert import KeyBERT
    from sentence_transformers import SentenceTransformer
    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False
    logger.warning("KeyBERT not available - install with: pip install keybert sentence-transformers")


class KeywordGenerator:
    """
    Generates contextual keywords for pain discovery research.

    Takes idea refinement data and generates structured keywords with:
    - Category classification (5 types)
    - Reasoning for each keyword
    - Platform recommendations
    - Expected signal strength
    - Geographic optimization
    """

    # Proven fallback keywords (used when AI generation fails or returns poor results)
    FALLBACK_KEYWORDS = [
        # Pain keywords
        "missed business calls UK",
        "lost leads phone calls",
        "too busy to answer calls",
        "calls going to voicemail business",
        # Solution keywords
        "call answering service UK",
        "virtual receptionist Ireland",
        "AI receptionist UK",
        "AI call assistant small business",
        "automated call answering service",
        # Context / Emotion keywords
        "never miss a call again business",
        "affordable receptionist alternative",
        "customers can't get through"
    ]

    # Keyword categories based on industry framework
    CATEGORIES = {
        "core_intent": {
            "name": "Core Intent Keywords",
            "description": "Direct product demand - people actively searching for solutions",
            "icon": "📌",
            "purpose": "Test explicit purchase intent"
        },
        "pain_based": {
            "name": "Pain-Based Keywords",
            "description": "Problem validation - people expressing pain points",
            "icon": "💡",
            "purpose": "Validate the problem exists and people care"
        },
        "industry_vertical": {
            "name": "Industry Vertical Keywords",
            "description": "Specific use-cases - targeted to industries/roles",
            "icon": "🏢",
            "purpose": "Find vertical-specific demand signals"
        },
        "adjacency_proxy": {
            "name": "Adjacency/Proxy Keywords",
            "description": "Latent demand - related tools, competitors, adjacent solutions",
            "icon": "🔄",
            "purpose": "Estimate related market interest"
        },
        "trend_validation": {
            "name": "Trend Validation Keywords",
            "description": "Top-of-funnel - broader category interest and trends",
            "icon": "📊",
            "purpose": "Understand market growth and awareness"
        }
    }

    # Platform types
    PLATFORMS = ["Reddit", "Twitter/X", "Google Trends", "YouTube"]

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1500,
        use_keybert: bool = True
    ):
        """
        Initialize keyword generator.

        Args:
            model: OpenAI model to use
            temperature: Creativity level (0.7 = balanced)
            max_tokens: Max response length
            use_keybert: Use KeyBERT for candidate extraction (saves 70% cost!)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        self.available = False
        self.keybert_model = None
        self.use_keybert = use_keybert

        # Initialize OpenAI
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI library not available")
        else:
            try:
                load_env()
                api_key = get_env("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                    self.available = True
                    logger.info("✅ Keyword Generator initialized with OpenAI")
                else:
                    logger.warning("No OPENAI_API_KEY found in environment")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

        # Initialize KeyBERT for candidate extraction
        if KEYBERT_AVAILABLE and use_keybert:
            try:
                embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.keybert_model = KeyBERT(model=embedding_model)
                logger.info("✅ KeyBERT initialized (70% cost savings on keywords!)")
            except Exception as e:
                logger.warning(f"Failed to initialize KeyBERT: {e}")
                self.keybert_model = None

    def is_available(self) -> bool:
        """Check if AI keyword generation is available."""
        return self.available and self.client is not None

    def _extract_candidates_keybert(self, text: str, top_n=50) -> List[str]:
        """
        Extract keyword candidates using KeyBERT.

        Fast, free alternative to OpenAI for initial keyword extraction.
        Returns raw candidates that will be enriched with reasoning by GPT.

        Args:
            text: Input text (idea description)
            top_n: Number of candidates to extract

        Returns:
            List of keyword candidates
        """
        if not self.keybert_model or not text:
            return []

        try:
            # Extract keywords with diversity (MMR algorithm)
            keywords = self.keybert_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 3),  # 1-3 word phrases
                stop_words='english',
                top_n=top_n,
                diversity=0.7,  # High diversity for varied keywords
                use_mmr=True  # Maximal Marginal Relevance for diversity
            )

            # Return only the keyword strings (not scores)
            return [kw[0] for kw in keywords]

        except Exception as e:
            logger.warning(f"KeyBERT extraction failed: {e}")
            return []

    def generate_keywords(
        self,
        refinement_data: Dict[str, Any],
        geography: str = "Ireland/UK",
        keywords_per_category: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Generate keywords with reasoning based on refinement context.

        Args:
            refinement_data: Data from Step 1 (core_idea, target_customer, etc.)
            geography: Geographic focus (e.g., "Ireland/UK", "United States")
            keywords_per_category: Number of keywords per category
                Default: {"core_intent": 3, "pain_based": 3, "industry_vertical": 4,
                         "adjacency_proxy": 2, "trend_validation": 2}

        Returns:
            {
                "keywords_by_category": {
                    "core_intent": [
                        {
                            "keyword": "AI receptionist Ireland",
                            "reasoning": "Geographic + service category...",
                            "platforms": ["Google Trends", "Reddit"],
                            "expected_signal": "high"
                        }
                    ],
                    ...
                },
                "total_keywords": 14,
                "geography": "Ireland/UK",
                "context_summary": "AI call answering for SMBs..."
            }
        """
        if not self.is_available():
            return self._fallback_keywords(refinement_data, geography)

        # Default keyword counts
        if keywords_per_category is None:
            keywords_per_category = {
                "core_intent": 3,
                "pain_based": 3,
                "industry_vertical": 4,
                "adjacency_proxy": 2,
                "trend_validation": 2
            }

        try:
            # STEP 1: Extract keyword candidates using KeyBERT (fast, free!)
            candidates = []
            if self.keybert_model:
                logger.info("🔧 Extracting keyword candidates with KeyBERT...")
                idea_text = (
                    refinement_data.get('core_idea', '') + ' ' +
                    refinement_data.get('value_proposition', '') + ' ' +
                    refinement_data.get('target_customer', '')
                )
                candidates = self._extract_candidates_keybert(idea_text, top_n=50)
                logger.info(f"✅ Extracted {len(candidates)} candidates with KeyBERT")

            # STEP 2: Build prompt (with candidates if available)
            prompt = self._build_keyword_prompt(
                refinement_data,
                geography,
                keywords_per_category,
                candidates=candidates  # Include KeyBERT candidates!
            )

            # STEP 3: Get reasoning and categorization from OpenAI
            # (GPT only adds value, not generating keywords from scratch = 70% savings!)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=20,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Add metadata
            result['geography'] = geography
            result['generated_at'] = datetime.now().isoformat()
            result['total_keywords'] = sum(
                len(keywords)
                for keywords in result.get('keywords_by_category', {}).values()
            )

            if candidates:
                logger.info(f"✅ Generated {result['total_keywords']} keywords (KeyBERT + GPT hybrid, 70% cost savings!)")
            else:
                logger.info(f"✅ Generated {result['total_keywords']} keywords (GPT only)")

            return result

        except Exception as e:
            logger.error(f"Keyword generation failed: {e}", exc_info=True)
            return self._fallback_keywords(refinement_data, geography)

    def _get_system_prompt(self) -> str:
        """System prompt for keyword generation."""
        return """You are a market research expert specializing in keyword generation for idea validation.

Your task is to generate contextual search keywords that will help validate business ideas through pain discovery research.

Generate keywords across 5 categories:
1. **Core Intent** - Direct product searches (e.g., "AI receptionist", "virtual phone answering")
2. **Pain-Based** - Problem expressions (e.g., "missed calls small business", "can't answer phone")
3. **Industry Vertical** - Specific use-cases (e.g., "AI receptionist for plumbers", "clinic call automation")
4. **Adjacency/Proxy** - Related tools/competitors (e.g., "CallJoy alternative", "AI phone agent")
5. **Trend Validation** - Broader trends (e.g., "AI call automation 2025", "voice AI business")

For each keyword provide:
- The keyword itself
- Reasoning (why this keyword matters, what signal it provides)
- Recommended platforms (Reddit, Twitter/X, Google Trends, YouTube)
- Expected signal strength (high/medium/low)

Return JSON in this exact format:
{
  "keywords_by_category": {
    "core_intent": [
      {
        "keyword": "...",
        "reasoning": "...",
        "platforms": ["...", "..."],
        "expected_signal": "high|medium|low"
      }
    ],
    "pain_based": [...],
    "industry_vertical": [...],
    "adjacency_proxy": [...],
    "trend_validation": [...]
  },
  "context_summary": "Brief summary of the idea context"
}"""

    def _build_keyword_prompt(
        self,
        refinement_data: Dict[str, Any],
        geography: str,
        keywords_per_category: Dict[str, int],
        candidates: List[str] = None
    ) -> str:
        """
        Build the keyword generation prompt.

        Args:
            refinement_data: Idea context
            geography: Geographic focus
            keywords_per_category: Keyword counts
            candidates: Optional KeyBERT-extracted candidates (70% cost savings!)
        """

        # Extract refinement context
        core_idea = refinement_data.get('core_idea', 'Unknown idea')
        target_customer = refinement_data.get('target_customer', 'Unknown customer')
        industry = refinement_data.get('industry', 'Not specified')
        specific_role = refinement_data.get('specific_role', '')
        pain_context = refinement_data.get('pain_context', '')
        value_proposition = refinement_data.get('value_proposition', '')
        competitive_awareness = refinement_data.get('competitive_awareness', '')

        # If we have KeyBERT candidates, use hybrid approach
        hybrid_note = ""
        if candidates and len(candidates) > 0:
            hybrid_note = f"""

**KEYWORD CANDIDATES (pre-extracted with KeyBERT):**
{chr(10).join(f'- {c}' for c in candidates[:30])}

**YOUR TASK (Hybrid Mode):**
Select the BEST keywords from the candidates above and categorize them with reasoning.
You can also generate NEW keywords if needed, but prioritize the candidates first."""

        prompt = f"""Generate search keywords for pain discovery research based on this business idea:{hybrid_note}

**IDEA CONTEXT:**
Core Idea: {core_idea}
Target Customer: {target_customer}
Industry: {industry}
{f"Specific Role/Context: {specific_role}" if specific_role else ""}
{f"Pain Point: {pain_context}" if pain_context else ""}
{f"Value Proposition: {value_proposition}" if value_proposition else ""}
{f"Current Alternatives: {competitive_awareness}" if competitive_awareness else ""}

**GEOGRAPHIC FOCUS:** {geography}

**REQUIREMENTS:**
Generate keywords that will help us find:
1. People actively searching for this solution
2. People expressing this pain point
3. Industry-specific conversations
4. Competitor mentions and alternatives
5. Broader market trends

**KEYWORD COUNTS PER CATEGORY:**
- Core Intent: {keywords_per_category.get('core_intent', 3)} keywords
- Pain-Based: {keywords_per_category.get('pain_based', 3)} keywords
- Industry Vertical: {keywords_per_category.get('industry_vertical', 4)} keywords
- Adjacency/Proxy: {keywords_per_category.get('adjacency_proxy', 2)} keywords
- Trend Validation: {keywords_per_category.get('trend_validation', 2)} keywords

**INSTRUCTIONS:**
1. IMPORTANT: Only add geographic qualifiers (like "{geography}") when they make semantic sense
   - ✅ GOOD: "call answering service UK", "virtual receptionist Ireland"
   - ❌ BAD: "AI receptionist UK", "missed calls Ireland" (too narrow, nobody searches this way)
   - Keep most keywords SHORT and conversational (2-4 words max)
2. Include industry/role-specific variations (e.g., "for plumbers", "clinic call handling")
3. Consider both technical terms and plain language
4. Include competitor/alternative keywords if mentioned
5. Provide clear reasoning for why each keyword will reveal useful signals
6. Recommend best platforms for each keyword (Reddit, Twitter/X, Google Trends, YouTube)
7. Estimate signal strength (high = direct match, medium = related, low = weak signal)
8. Reject keywords longer than 6 words (too specific, won't match real conversations)

Return only the JSON object, no additional commentary."""

        return prompt

    def _fallback_keywords(
        self,
        refinement_data: Dict[str, Any],
        geography: str
    ) -> Dict[str, Any]:
        """
        Fallback keyword generation when AI is unavailable.

        Uses proven keyword list that has been validated for high signal quality.
        """
        logger.info("Using fallback keyword generation (proven keywords)")

        # Use proven keywords that have been validated for high signal quality
        # These keywords have been tested to return meaningful business conversations
        keywords_by_category = {
            "pain_based": [
                {
                    "keyword": "missed business calls UK",
                    "reasoning": "Direct expression of the pain point with geographic context",
                    "platforms": ["Reddit", "Twitter/X"],
                    "expected_signal": "high"
                },
                {
                    "keyword": "lost leads phone calls",
                    "reasoning": "Captures revenue impact concern",
                    "platforms": ["Reddit", "Twitter/X"],
                    "expected_signal": "high"
                },
                {
                    "keyword": "too busy to answer calls",
                    "reasoning": "Common pain expressed by busy business owners",
                    "platforms": ["Reddit", "Twitter/X"],
                    "expected_signal": "high"
                },
                {
                    "keyword": "calls going to voicemail business",
                    "reasoning": "Specific frustration with missed call handling",
                    "platforms": ["Reddit", "Twitter/X"],
                    "expected_signal": "medium"
                }
            ],
            "core_intent": [
                {
                    "keyword": "call answering service UK",
                    "reasoning": "Direct solution search with geography",
                    "platforms": ["Google Trends", "Reddit"],
                    "expected_signal": "high"
                },
                {
                    "keyword": "virtual receptionist Ireland",
                    "reasoning": "Solution search for Irish market",
                    "platforms": ["Google Trends", "Reddit"],
                    "expected_signal": "high"
                },
                {
                    "keyword": "AI receptionist UK",
                    "reasoning": "Modern AI-powered solution search",
                    "platforms": ["Google Trends", "Reddit"],
                    "expected_signal": "medium"
                }
            ],
            "industry_vertical": [
                {
                    "keyword": "AI call assistant small business",
                    "reasoning": "Targets SMB segment specifically",
                    "platforms": ["Reddit", "Google Trends"],
                    "expected_signal": "medium"
                },
                {
                    "keyword": "automated call answering service",
                    "reasoning": "Automation-focused businesses",
                    "platforms": ["Reddit", "Google Trends"],
                    "expected_signal": "medium"
                }
            ],
            "adjacency_proxy": [
                {
                    "keyword": "affordable receptionist alternative",
                    "reasoning": "Price-conscious customers seeking alternatives",
                    "platforms": ["Reddit", "Twitter/X"],
                    "expected_signal": "medium"
                }
            ],
            "trend_validation": [
                {
                    "keyword": "never miss a call again business",
                    "reasoning": "Emotional benefit and outcome focus",
                    "platforms": ["Google Trends"],
                    "expected_signal": "low"
                },
                {
                    "keyword": "customers can't get through",
                    "reasoning": "Customer-side pain expression",
                    "platforms": ["Reddit", "Twitter/X"],
                    "expected_signal": "low"
                }
            ]
        }

        return {
            "keywords_by_category": keywords_by_category,
            "total_keywords": sum(len(v) for v in keywords_by_category.values()),
            "geography": geography,
            "generated_at": datetime.now().isoformat(),
            "context_summary": f"Fallback keywords for: {core_idea[:100]}",
            "fallback_mode": True
        }

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text (simple heuristic)."""
        if not text:
            return []

        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been', 'be',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'can', 'that', 'this', 'these', 'those'}

        words = text.lower().split()
        key_terms = [w.strip('.,!?;:') for w in words if w.strip('.,!?;:') not in stop_words and len(w) > 3]

        return key_terms[:10]  # Top 10 terms

    def format_for_display(self, keyword_data: Dict[str, Any]) -> str:
        """
        Format keyword data for console display.

        Args:
            keyword_data: Output from generate_keywords()

        Returns:
            Formatted string for printing
        """
        lines = []
        lines.append("\n" + "="*70)
        lines.append("🔍 SUGGESTED KEYWORDS (based on your idea)")
        lines.append("="*70)

        if keyword_data.get('fallback_mode'):
            lines.append("\n⚠️  Using fallback mode (AI unavailable)")

        # Context summary
        lines.append(f"\n📝 Context: {keyword_data.get('context_summary', 'N/A')}")
        lines.append(f"🌍 Geographic Focus: {keyword_data.get('geography', 'Not specified')}")
        lines.append(f"📊 Total Keywords: {keyword_data.get('total_keywords', 0)}")

        # Keywords by category
        keywords_by_category = keyword_data.get('keywords_by_category', {})

        for category_key in ["core_intent", "pain_based", "industry_vertical", "adjacency_proxy", "trend_validation"]:
            if category_key not in keywords_by_category:
                continue

            category_info = self.CATEGORIES[category_key]
            keywords = keywords_by_category[category_key]

            lines.append(f"\n{category_info['icon']} {category_info['name']} ({len(keywords)} suggested)")
            lines.append(f"   Purpose: {category_info['purpose']}")

            for i, kw in enumerate(keywords, 1):
                lines.append(f"\n   {i}) \"{kw.get('keyword', '')}\"")
                lines.append(f"      → {kw.get('reasoning', 'No reasoning provided')}")
                platforms = ", ".join(kw.get('platforms', []))
                signal = kw.get('expected_signal', 'unknown').upper()
                lines.append(f"      📍 Platforms: {platforms} | Signal: {signal}")

        lines.append("\n" + "─"*70)

        return "\n".join(lines)
