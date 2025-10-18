"""
Workflow Gates - Conversational gated workflow system.

Defines workflow steps with natural conversation prompts, soft validation,
and educational context for guiding users through idea development.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

# ============================================================================
# WORKFLOW STEP DEFINITIONS
# ============================================================================

WORKFLOW_STEPS = {
    "step_1_refinement": {
        "name": "Idea Refinement",
        "description": "Let's explore and refine your idea together",
        "education": """
🎯 **Why This Matters**
This conversation helps me understand your idea deeply so I can give you the best research and insights.
The more context you share, the better I can help identify opportunities and challenges.
        """,
        "priority": "CRITICAL",
        "requirements": {
            "core_idea": {
                "prompt": "Tell me about your idea. What problem are you trying to solve?",
                "conversation_starters": [
                    "What inspired this idea?",
                    "What problem keeps coming up that you want to solve?",
                    "Tell me what you're thinking about building."
                ],
                "follow_ups": {
                    "problem_depth": {
                        "prompt": "That's interesting! Can you tell me more about why this problem matters?",
                        "triggers": ["short_answer", "vague"],
                    },
                    "solution_vision": {
                        "prompt": "How do you imagine solving this? What would success look like?",
                        "triggers": ["has_problem_no_solution"],
                    }
                },
                "validation": {
                    "min_length": 20,
                    "warn_if_vague": ["something", "stuff", "things", "idea"],
                    "confidence_factors": ["problem_mentioned", "solution_mentioned", "user_mentioned"],
                    "gentle_suggestions": [
                        "Could you tell me a bit more about who experiences this problem?",
                        "What made you think of this particular solution?",
                        "Have you seen others trying to solve this?"
                    ]
                }
            },
            "target_customer": {
                "prompt": "Who is this for? Who would benefit most from this?",
                "conversation_starters": [
                    "I'm thinking this could help: small businesses, large enterprises, individual consumers, or developers. Which feels closest?",
                    "Tell me about the person who has this problem.",
                    "Who do you imagine using this?"
                ],
                "options": [
                    "Small businesses (1-50 employees)",
                    "Mid-market companies (50-500 employees)",
                    "Large enterprises (500+ employees)",
                    "Individual consumers (B2C)",
                    "Developers/technical users",
                    "Let me describe them..."
                ],
                "follow_ups": {
                    "industry": {
                        "prompt": "What industry are they in?",
                        "triggers": ["selected_business"],
                        "options": ["Tech/SaaS", "Healthcare", "Finance", "Retail", "Manufacturing", "Education", "Other"]
                    },
                    "specific_role": {
                        "prompt": "What's their role? What do they do day-to-day?",
                        "triggers": ["always"],
                    },
                    "pain_context": {
                        "prompt": "When does this problem hit them hardest?",
                        "triggers": ["has_role"],
                    }
                },
                "validation": {
                    "min_length": 15,
                    "warn_if_vague": ["people", "users", "everyone", "anyone"],
                    "confidence_factors": ["industry_mentioned", "role_mentioned", "company_size_mentioned"],
                    "gentle_suggestions": [
                        "It helps to be specific about who they are. What industry? What role?",
                        "Could you paint me a picture of a specific person who has this problem?"
                    ]
                }
            },
            "value_proposition": {
                "prompt": "What makes your solution different or better than what exists today?",
                "conversation_starters": [
                    "What's special about your approach?",
                    "Why would someone choose this over alternatives?",
                    "What's the key insight that makes this work?"
                ],
                "follow_ups": {
                    "competitive_awareness": {
                        "prompt": "What alternatives do people use today to solve this?",
                        "triggers": ["always"],
                    },
                    "key_differentiator": {
                        "prompt": "If you had to pick one thing that makes this better, what would it be?",
                        "triggers": ["multiple_benefits"],
                    }
                },
                "validation": {
                    "min_length": 20,
                    "warn_if_vague": ["better", "easier", "faster"],
                    "confidence_factors": ["specific_benefit", "comparison_mentioned", "metric_mentioned"],
                    "gentle_suggestions": [
                        "Can you be more specific about how it's better?",
                        "What would someone notice immediately that's different?"
                    ]
                }
            },
            "timeline": {
                "prompt": "What's your timeline? Are you exploring, building, or ready to launch?",
                "conversation_starters": [
                    "Where are you at with this?",
                    "Is this a new idea you're exploring, or have you started building?",
                    "When would you like to have something ready?"
                ],
                "options": [
                    "Just exploring - very early stage",
                    "Validated the idea - planning to build",
                    "Currently building - need market validation",
                    "Built something - ready to launch",
                    "Already launched - looking to grow"
                ],
                "follow_ups": {
                    "urgency": {
                        "prompt": "What's driving your timeline?",
                        "triggers": ["has_deadline"],
                    }
                },
                "validation": {
                    "min_length": 10,
                    "confidence_factors": ["stage_mentioned", "timeframe_mentioned"],
                    "gentle_suggestions": [
                        "Knowing your timeline helps me prioritize what research matters most."
                    ]
                }
            }
        },
        "completion_threshold": 0.5,  # Soft - 50% confidence to proceed
        "summary_template": """
📋 **Here's what I understand so far:**

**Your Idea:** {core_idea}

**Target Customer:** {target_customer}

**What Makes It Special:** {value_proposition}

**Timeline:** {timeline}

**Confidence:** {confidence_bar} {confidence_pct}%

{warnings}

Does this capture your idea? Would you like to refine anything, or shall we move to research?
        """
    },

    "step_2_pain_discovery": {
        "name": "Pain Discovery & Validation",
        "description": "Let's validate this problem is real and widespread",
        "education": """
🔍 **Why This Matters**
Before building anything, we need to confirm people actually have this problem and care enough to pay for a solution.
This research will show us real conversations, pain points, and whether there's genuine demand.
        """,
        "priority": "CRITICAL",
        "auto_trigger": True,  # Automatically runs research agents
        "requirements": {
            "research_sources": {
                "prompt": "Where should I look for people talking about this problem?",
                "conversation_starters": [
                    "I can search Reddit communities, X/Twitter, YouTube, or Google Trends. Which would be most relevant?",
                    "Where does your target customer hang out online?",
                    "What communities or forums discuss this topic?"
                ],
                "options": [
                    "Reddit (specific subreddits)",
                    "X/Twitter conversations",
                    "YouTube videos/comments",
                    "All of the above"
                ],
                "follow_ups": {
                    "specific_subreddits": {
                        "prompt": "Which subreddits should I check?",
                        "triggers": ["selected_reddit"],
                        "gentle_suggestions": ["Not sure? I can suggest based on your target customer."]
                    },
                    "keywords": {
                        "prompt": "What keywords or phrases would people use when talking about this problem?",
                        "triggers": ["always"],
                    }
                }
            }
        },
        "completion_threshold": 0.3,  # Very soft - mainly automatic
        "summary_template": """
🔍 **Pain Discovery Research**

**Sources:** {research_sources}
**Keywords:** {keywords}

I'll now search these sources for real pain points and conversations. This usually takes 2-3 minutes.

Ready to start the research?
        """
    },

    "step_3_market_sizing": {
        "name": "Market Sizing",
        "description": "Let's understand the market opportunity",
        "education": """
📊 **Why This Matters**
Understanding market size helps us know if this is a niche solution or a massive opportunity.
It also reveals trends - is this market growing, stable, or shrinking?
        """,
        "priority": "HIGH",
        "auto_trigger": True,
        "requirements": {
            "geography": {
                "prompt": "Where are you targeting? Local, national, or global?",
                "options": [
                    "United States",
                    "North America",
                    "Europe",
                    "Global",
                    "Specific region..."
                ]
            }
        },
        "completion_threshold": 0.3,
        "summary_template": """
📊 **Market Sizing Research**

**Geography:** {geography}
**Target Customer:** {target_customer}

I'll research market size, trends, and growth data.

Ready to proceed?
        """
    },

    "step_4_competitive_landscape": {
        "name": "Competitive Analysis",
        "description": "Let's see who else is in this space",
        "education": """
⚔️ **Why This Matters**
Understanding competitors helps you position better, find gaps, and learn from what's working.
Competition is usually a good sign - it means there's a real market.
        """,
        "priority": "HIGH",
        "auto_trigger": True,
        "requirements": {
            "known_competitors": {
                "prompt": "Do you know of any competitors or alternatives?",
                "conversation_starters": [
                    "What tools or solutions do people use today?",
                    "Have you seen anyone else trying to solve this?",
                    "It's okay if you don't know - I can find them."
                ],
                "optional": True
            }
        },
        "completion_threshold": 0.2,
        "summary_template": """
⚔️ **Competitive Analysis**

**Known Competitors:** {known_competitors}

I'll search for direct competitors, alternatives, and adjacent solutions.

Ready to proceed?
        """
    }
}


# ============================================================================
# SOFT VALIDATION FUNCTIONS
# ============================================================================

def validate_field(field_config: Dict[str, Any], value: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Soft validation - ALWAYS valid, but provides confidence score and gentle suggestions.

    Args:
        field_config: Configuration from WORKFLOW_STEPS
        value: User's input
        context: Other collected data for contextual validation

    Returns:
        {
            "valid": True (always),
            "confidence": 0.0-1.0,
            "warnings": [],
            "suggestions": []
        }
    """
    context = context or {}
    validation = field_config.get('validation', {})

    result = {
        "valid": True,  # ALWAYS valid in soft mode
        "confidence": 0.5,  # Start at 50%
        "warnings": [],
        "suggestions": []
    }

    # Check minimum length
    min_length = validation.get('min_length', 10)
    if len(value.strip()) < min_length:
        result['confidence'] -= 0.2
        result['warnings'].append(f"⚠️ Short answer (under {min_length} characters)")
        if validation.get('gentle_suggestions'):
            result['suggestions'].append(validation['gentle_suggestions'][0])

    # Check for vague terms
    vague_terms = validation.get('warn_if_vague', [])
    value_lower = value.lower()
    found_vague = [term for term in vague_terms if term in value_lower]
    if found_vague:
        result['confidence'] -= 0.15
        result['warnings'].append(f"⚠️ Vague terms: {', '.join(found_vague)}")
        if len(validation.get('gentle_suggestions', [])) > 1:
            result['suggestions'].append(validation['gentle_suggestions'][1])

    # Check confidence factors (boost confidence if present)
    confidence_factors = validation.get('confidence_factors', [])
    for factor in confidence_factors:
        if _has_factor(value, factor):
            result['confidence'] += 0.15

    # Cap confidence at 1.0
    result['confidence'] = min(1.0, max(0.0, result['confidence']))

    return result


def _has_factor(text: str, factor: str) -> bool:
    """Check if text contains confidence factor."""
    text_lower = text.lower()

    factor_patterns = {
        "problem_mentioned": ["problem", "issue", "challenge", "struggle", "difficult", "pain"],
        "solution_mentioned": ["solve", "fix", "help", "improve", "build", "create", "make"],
        "user_mentioned": ["user", "customer", "people", "business", "company", "person"],
        "industry_mentioned": ["industry", "healthcare", "finance", "tech", "retail", "education"],
        "role_mentioned": ["manager", "engineer", "developer", "owner", "ceo", "founder", "director"],
        "company_size_mentioned": ["small", "large", "enterprise", "startup", "employees"],
        "specific_benefit": ["save", "reduce", "increase", "faster", "better", "cheaper", "%", "x"],
        "comparison_mentioned": ["than", "instead", "unlike", "compared", "alternative"],
        "metric_mentioned": ["hour", "day", "week", "month", "$", "cost", "revenue", "%"],
        "stage_mentioned": ["exploring", "building", "launched", "planning", "validating"],
        "timeframe_mentioned": ["month", "quarter", "year", "soon", "2024", "2025"]
    }

    patterns = factor_patterns.get(factor, [])
    return any(pattern in text_lower for pattern in patterns)


def calculate_step_completion(step_config: Dict[str, Any], collected_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate completion score for a step based on collected data.

    Returns:
        {
            "score": 0.0-1.0,
            "field_scores": {...},
            "can_proceed": True/False,
            "warnings": [],
            "encouragement": ""
        }
    """
    requirements = step_config.get('requirements', {})
    field_scores = {}
    total_confidence = 0
    field_count = 0

    for field_name, field_config in requirements.items():
        value = collected_data.get(field_name, "")

        # Skip optional fields if not provided
        if not value and field_config.get('optional'):
            continue

        validation_result = validate_field(field_config, value, collected_data)
        field_scores[field_name] = validation_result['confidence']
        total_confidence += validation_result['confidence']
        field_count += 1

    avg_score = total_confidence / field_count if field_count > 0 else 0
    threshold = step_config.get('completion_threshold', 0.5)

    result = {
        "score": avg_score,
        "field_scores": field_scores,
        "can_proceed": True,  # ALWAYS can proceed in soft mode
        "warnings": [],
        "encouragement": ""
    }

    # Add warnings based on score
    if avg_score < 0.3:
        result['warnings'].append("⚠️ Low detail - I'll do my best, but more context would help me give better insights.")
    elif avg_score < threshold:
        result['warnings'].append("⚠️ Some details are light - consider adding more for better results.")
    else:
        result['encouragement'] = "✅ Great! I have good context to work with."

    return result


def format_confidence_bar(confidence: float) -> str:
    """Format confidence as a visual bar."""
    filled = int(confidence * 10)
    empty = 10 - filled
    return f"[{'█' * filled}{'░' * empty}]"


def get_step_order() -> List[str]:
    """Return ordered list of workflow steps."""
    return [
        "step_1_refinement",
        "step_2_pain_discovery",
        "step_3_market_sizing",
        "step_4_competitive_landscape"
    ]


def get_step_config(step_name: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific step."""
    return WORKFLOW_STEPS.get(step_name)
