from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class LocationAnalyzerCrew:
    """Location Analyzer Crew - Hierarchical process for geospatial analysis.
    
    This crew handles the Intelligence Phase:
    - Manager assigns approved properties (max 4) to analyzer agents
    - Each analyzer handles ALL 8 amenity types for one property
    - Analyzers work in parallel using async_execution
    - Report agent compiles results to JSON
    
    Process: Hierarchical - Manager coordinates parallel property analysis.
    
    Amenity Types (6km radius):
    - Markets, Gyms, Bus parks, Railway terminals
    - Stadiums, Malls, Airports, Seaports
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def manager(self) -> Agent:
        """Manager agent that coordinates property assignments."""
        return Agent(
            config=self.agents_config["manager"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def location_analyzer_1(self) -> Agent:
        """Location analyzer for property 1."""
        return Agent(
            config=self.agents_config["location_analyzer_1"],  # type: ignore[index]
            reasoning=True,  # Enable reasoning for multi-factor analysis
            max_reasoning_attempts=2,
            respect_context_window=True,  # Summarize large outputs
            verbose=True,
            # tools=[google_maps_tool],  # TODO: Add Google Maps tool
        )

    @agent
    def location_analyzer_2(self) -> Agent:
        """Location analyzer for property 2."""
        return Agent(
            config=self.agents_config["location_analyzer_2"],  # type: ignore[index]
            reasoning=True,
            max_reasoning_attempts=2,
            respect_context_window=True,
            verbose=True,
        )

    @agent
    def location_analyzer_3(self) -> Agent:
        """Location analyzer for property 3."""
        return Agent(
            config=self.agents_config["location_analyzer_3"],  # type: ignore[index]
            reasoning=True,
            max_reasoning_attempts=2,
            respect_context_window=True,
            verbose=True,
        )

    @agent
    def location_analyzer_4(self) -> Agent:
        """Location analyzer for property 4."""
        return Agent(
            config=self.agents_config["location_analyzer_4"],  # type: ignore[index]
            reasoning=True,
            max_reasoning_attempts=2,
            respect_context_window=True,
            verbose=True,
        )

    @agent
    def report_agent(self) -> Agent:
        """Report agent that compiles location intelligence to JSON."""
        return Agent(
            config=self.agents_config["report_agent"],  # type: ignore[index]
            verbose=True,
        )

    @task
    def assign_properties(self) -> Task:
        """Task for manager to assign properties to analyzers."""
        return Task(
            config=self.tasks_config["assign_properties"],  # type: ignore[index]
        )

    @task
    def analyze_property_1(self) -> Task:
        """Async task for analyzer 1."""
        return Task(
            config=self.tasks_config["analyze_property_1"],  # type: ignore[index]
            async_execution=True,
        )

    @task
    def analyze_property_2(self) -> Task:
        """Async task for analyzer 2."""
        return Task(
            config=self.tasks_config["analyze_property_2"],  # type: ignore[index]
            async_execution=True,
        )

    @task
    def analyze_property_3(self) -> Task:
        """Async task for analyzer 3."""
        return Task(
            config=self.tasks_config["analyze_property_3"],  # type: ignore[index]
            async_execution=True,
        )

    @task
    def analyze_property_4(self) -> Task:
        """Async task for analyzer 4."""
        return Task(
            config=self.tasks_config["analyze_property_4"],  # type: ignore[index]
            async_execution=True,
        )

    @task
    def compile_location_report(self) -> Task:
        """Task to compile all location analysis into JSON report."""
        return Task(
            config=self.tasks_config["compile_location_report"],  # type: ignore[index]
            output_file="output/location_intelligence.json",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Location Analyzer Crew with hierarchical process."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm="gpt-4o",
            memory=True,
            verbose=True,
        )
