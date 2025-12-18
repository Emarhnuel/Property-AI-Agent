import os
from typing import List

from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

llm = LLM(
    model="openrouter/deepseek/deepseek-r1",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.1,
    #stream=True
)

@CrewBase
class ResearchCrew:
    """Research Agent Crew - Sequential process for property discovery.
    
    This crew handles the Deep Discovery phase:
    1. Scraper - Finds listings on real estate platforms
    2. Data Extractor - Structures property data
    3. Validator - Ensures data quality
    4. Report Agent - Compiles JSON for Human Decision Gate
    
    Process: Sequential - Each step depends on the previous output.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def scraper(self) -> Agent:
        """Scraper agent that finds property listings."""
        return Agent(
            config=self.agents_config["scraper"],  # type: ignore[index]
            verbose=True,
            llm=llm,
            max_iter=10,
            # tools=[firecrawl_tool],  # TODO: Add Firecrawl tool
        )

    @agent
    def data_extractor(self) -> Agent:
        """Data extractor agent that structures property data."""
        return Agent(
            config=self.agents_config["data_extractor"],  # type: ignore[index]
            verbose=True,
            max_iter=6,
            llm=llm
        )

    @agent
    def validator(self) -> Agent:
        """Validator agent that ensures data quality."""
        return Agent(
            config=self.agents_config["validator"],  # type: ignore[index]
            verbose=True,
            max_iter=3,
            llm=llm 
        )

    @agent
    def report_agent(self) -> Agent:
        """Report agent that compiles results to JSON."""
        return Agent(
            config=self.agents_config["report_agent"],  # type: ignore[index]
            verbose=True,
            max_iter=5,
            llm=llm 
        )

    @task
    def scrape_listings(self) -> Task:
        """Task to scrape property listings from platforms."""
        return Task(
            config=self.tasks_config["scrape_listings"],  # type: ignore[index]
        )

    @task
    def extract_property_data(self) -> Task:
        """Task to extract structured data from raw listings."""
        return Task(
            config=self.tasks_config["extract_property_data"],  # type: ignore[index]
        )

    @task
    def validate_data(self) -> Task:
        """Task to validate extracted property data."""
        return Task(
            config=self.tasks_config["validate_data"],  # type: ignore[index]
        )

    @task
    def compile_research_report(self) -> Task:
        """Task to compile validated data into JSON report."""
        return Task(
            config=self.tasks_config["compile_research_report"],  # type: ignore[index]
            output_file="output/research_results.json",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew with sequential process."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            planning=True,  # Enable planning for scraping strategy
            verbose=True,
        )
