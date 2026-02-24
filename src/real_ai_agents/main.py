#!/usr/bin/env python
"""AI Real Estate Agent Flow - Find, Approve & Act"""

import json
import asyncio
from typing import List, Optional

from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, or_
from crewai.flow.persistence import persist
from crewai.flow.human_feedback import human_feedback, HumanFeedbackResult

from real_ai_agents.crews.research_crew.research_crew import ResearchCrew
from real_ai_agents.crews.call_agent_crew.call_agent_crew import CallAgentCrew
from real_ai_agents.crews.location_analyzer_crew.location_analyzer_crew import LocationAnalyzerCrew


# ========================= STATE =========================

class SearchCriteria(BaseModel):
    location: str
    property_type: str = "apartment"
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    max_price: Optional[float] = None
    rent_frequency: str = "monthly"
    additional_requirements: Optional[str] = None


class RealEstateState(BaseModel):
    search_criteria: Optional[SearchCriteria] = None
    approved_property_ids: List[str] = []
    retry_count: int = 0

    research_results: Optional[str] = None
    filtered_research_results: Optional[str] = None
    location_results: Optional[str] = None
    call_results: Optional[str] = None

    properties_found: int = 0
    properties_approved: int = 0


# ========================= FLOW =========================

@persist
class RealEstateFlow(Flow[RealEstateState]):

    @start()
    def initialize_search(self, search_criteria: SearchCriteria):
        """Take user search criteria and store in state."""
        print("\n🏠 AI Real Estate Agent")
        print("=" * 50)

        self.state.search_criteria = search_criteria

        print(f"Location: {search_criteria.location}")
        print(f"Type: {search_criteria.property_type}")
        if search_criteria.bedrooms:
            print(f"Bedrooms: {search_criteria.bedrooms}")

    # -------------------------
    # PHASE 1 — RESEARCH
    # -------------------------

    @listen(initialize_search)
    def run_research(self):
        """Kick off ResearchCrew with user's search criteria."""
        criteria = self.state.search_criteria

        search_query = f"{criteria.bedrooms or ''} bedroom {criteria.property_type} in {criteria.location}"
        if criteria.max_price:
            search_query += f" under {criteria.max_price}"
        search_query += f" ({criteria.rent_frequency} rent)"

        print(f"\n🔍 Searching: {search_query.strip()}")

        result = ResearchCrew().crew().kickoff(inputs={
            "search_criteria": search_query.strip(),
        })

        self.state.research_results = result.raw

        try:
            data = json.loads(result.raw)
            key = "properties" if "properties" in data else "listings"
            if key in data:
                self.state.properties_found = len(data[key])
        except Exception:
            pass

        print(f"✅ Found {self.state.properties_found} properties")
        return self.state.research_results

    # -------------------------
    # HUMAN APPROVAL
    # -------------------------

    @human_feedback(
        message="Review the properties above. Enter approved property IDs (e.g. ['prop_001','prop_002']) or type 'retry' to search again.",
        emit=["approved", "retry"],
        llm="openrouter/openai/gpt-4o-mini",
        default_outcome="approved",
    )
    @listen(or_("run_research", "retry"))
    def await_approval(self):
        """Show research results and wait for human approval."""
        return self.state.research_results

    @listen("approved")
    def filter_approved(self, result: HumanFeedbackResult):
        """Filter properties to only the ones the user approved."""
        try:
            approved_ids = json.loads(result.feedback)
            self.state.approved_property_ids = approved_ids
        except Exception:
            self.state.approved_property_ids = []

        try:
            data = json.loads(self.state.research_results)
            key = "properties" if "properties" in data else "listings"
            if key in data:
                data[key] = [
                    p for p in data[key]
                    if p.get("id") in self.state.approved_property_ids
                ]
                self.state.properties_approved = len(data[key])

            self.state.filtered_research_results = json.dumps(data)
        except Exception:
            self.state.filtered_research_results = self.state.research_results

        print(f"✅ {self.state.properties_approved} properties approved")

    @listen("retry")
    def handle_retry(self, result: HumanFeedbackResult):
        """Re-run research when user rejects results."""
        self.state.retry_count += 1
        print(f"\n🔄 Retry #{self.state.retry_count} — re-running research...")

    # -------------------------
    # PHASE 2 — PARALLEL (Call + Location)
    # -------------------------

    @listen(filter_approved)
    async def run_parallel_crews(self):
        """Run CallAgentCrew and LocationAnalyzerCrew in parallel."""
        if self.state.properties_approved == 0:
            print("⚠️ No properties approved, skipping.")
            return

        inputs = {"research_results": self.state.filtered_research_results}

        print("\n🚀 Running Call Agent & Location Analyzer in parallel...")

        call_task = asyncio.create_task(
            CallAgentCrew().crew().kickoff_async(inputs=inputs)
        )
        location_task = asyncio.create_task(
            LocationAnalyzerCrew().crew().kickoff_async(inputs=inputs)
        )

        call_result, location_result = await asyncio.gather(call_task, location_task)

        self.state.call_results = call_result.raw
        self.state.location_results = location_result.raw

        print("✅ Both crews completed")

    # -------------------------
    # FINAL REPORT
    # -------------------------

    @listen(run_parallel_crews)
    def compile_final_report(self):
        """Compile unified report from all phases."""
        final_report = {
            "search_criteria": self.state.search_criteria.model_dump(),
            "summary": {
                "properties_found": self.state.properties_found,
                "properties_approved": self.state.properties_approved,
                "retries": self.state.retry_count,
            },
            "approved_property_ids": self.state.approved_property_ids,
            "phases": {
                "research": self.state.research_results,
                "calls": self.state.call_results,
                "location": self.state.location_results,
            },
        }

        with open("output/unified_report.json", "w") as f:
            json.dump(final_report, f, indent=2)

        print("\n📋 Final report saved to output/unified_report.json")
        print("✅ Flow Complete")
        return final_report


# ========================= ENTRY POINTS =========================

def kickoff():
    """Run the flow."""
    RealEstateFlow().kickoff()


def plot():
    """Visualize the flow."""
    RealEstateFlow().plot()


if __name__ == "__main__":
    kickoff()
