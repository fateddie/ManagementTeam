"""
workshop_agent/__init__.py

Iterative Workshop Agent Package
Phase 1.1 - Workshop Agent Implementation

Purpose:
    Provides IterativeWorkshopAgent class that implements 3-round methodology:
    1. Quick Assessment (5 min) - Market context, top 3 risks/opportunities
    2. Risk Mitigation (5 min) - Address biggest risks with solutions  
    3. Opportunity Capture (5 min) - Optimize for biggest opportunities

Key Features:
    - Inherits from BaseAgent for orchestrator compatibility
    - Integrates Perplexity for real-time market data
    - Uses specific MBA + startup founder persona
    - Implements collaborative iteration methodology
    - Provides structured AgentOutput for downstream agents

Reasoning for Design:
    - Modular structure follows existing agent patterns (refinement_agent/, etc.)
    - BaseAgent inheritance ensures orchestrator compatibility without refactoring
    - Perplexity integration provides competitive advantage over static data
    - 3-round methodology balances thoroughness with user engagement
    - Specific persona builds trust and credibility for high-stakes decisions

Created: 2025-01-XX
"""

from .workshop_agent import IterativeWorkshopAgent

__all__ = ["IterativeWorkshopAgent"]
