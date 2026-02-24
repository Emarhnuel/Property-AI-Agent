"""
Custom Tools for AI Real Estate Agent.

This module exports all custom tools used by the crews:
- Retell AI tools for Voice AI calls (Inspector/Negotiator)
- Firecrawl tools for web scraping (Research Crew) - TODO
- Google Maps tools for location analysis (Location Analyzer Crew) - TODO
"""


from real_ai_agents.tools.retell_tools import (
    make_inspection_call,
    make_negotiation_call,
    get_call_result,
    check_call_status,
)

__all__ = [
    # Retell AI Voice Call Tools
    "make_inspection_call",
    "make_negotiation_call",
    "get_call_result",
    "check_call_status",
]
