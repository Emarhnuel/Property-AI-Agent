"""AI Real Estate Agent Crews.

This package contains the three main crews for the real estate workflow:

1. ResearchCrew - Sequential process for property discovery and data extraction
2. LocationAnalyzerCrew - Hierarchical process for geospatial amenity analysis  
3. CallAgentCrew - Hierarchical process for voice AI interactions

Each crew outputs JSON files that are consumed by the next phase via Flow @listen decorators.
"""

from real_ai_agents.crews.research_crew.research_crew import ResearchCrew
from real_ai_agents.crews.location_analyzer_crew.location_analyzer_crew import LocationAnalyzerCrew
from real_ai_agents.crews.call_agent_crew.call_agent_crew import CallAgentCrew

__all__ = [
    "ResearchCrew",
    "LocationAnalyzerCrew", 
    "CallAgentCrew",
]
