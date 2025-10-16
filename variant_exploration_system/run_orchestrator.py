#!/usr/bin/env python3
"""
Variant Exploration System - Main Entry Point
---------------------------------------------
Wrapper script that calls the modular orchestrator_core.py

Usage:
    python run_orchestrator.py
    python run_orchestrator.py --variant my_variant
    python run_orchestrator.py --compare
"""

import sys
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent / "orchestrator"))

# Import and run
from orchestrator_core import main

if __name__ == "__main__":
    main()

