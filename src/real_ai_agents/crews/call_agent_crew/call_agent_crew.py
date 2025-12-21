from typing import List
import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from src.real_ai_agents.tools.retell_tools import (
    make_inspection_call,
    make_negotiation_call,
    get_call_result,
    check_call_status,
)


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

llm = LLM(
    model="openrouter/deepseek/deepseek-chat",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.1,
)



@CrewBase
class CallAgentCrew:
    """Call Agent Crew - Hierarchical process for voice AI interactions.
    
    This crew handles phone calls to property agents (Inspector path) or 
    property owners (Negotiator path) based on user engagement intent.
    
    Process: Hierarchical - Manager routes calls to appropriate specialists.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def manager(self) -> Agent:
        """Manager agent that coordinates call routing."""
        return Agent(
            config=self.agents_config["manager"],  # type: ignore[index]
            verbose=True,
            llm=llm,
            max_iter=8,
            cache=True,
        )

    @agent
    def inspector(self) -> Agent:
        """Inspector agent for booking property viewings (rent/buy intent)."""
        return Agent(
            config=self.agents_config["inspector"],  # type: ignore[index]
            verbose=True,
            llm=llm,
            max_iter=10,
            max_rpm=10,
            cache=True,
            max_retry_limit=3,
            tools=[make_inspection_call, get_call_result, check_call_status],
        )

    @agent
    def negotiator(self) -> Agent:
        """Negotiator agent for acquisition discussions (acquisition intent)."""
        return Agent(
            config=self.agents_config["negotiator"],  # type: ignore[index]
            reasoning=True,  # Enable reasoning for complex persuasion strategies
            max_reasoning_attempts=3,
            verbose=True,
            llm=llm,
            max_iter=10,
            max_rpm=10,
            cache=True,
            max_retry_limit=3,
            tools=[make_negotiation_call, get_call_result, check_call_status],
        )

    @agent
    def report_agent(self) -> Agent:
        """Report agent that compiles call results to JSON."""
        return Agent(
            config=self.agents_config["report_agent"],  # type: ignore[index]
            verbose=True,
            llm=llm,
            max_iter=5,
            cache=True,
        )

    @task
    def route_calls(self) -> Task:
        """Task to route calls based on engagement intent."""
        return Task(
            config=self.tasks_config["route_calls"],  # type: ignore[index]
        )

    @task
    def conduct_inspection_calls(self) -> Task:
        """Task for Inspector to conduct calls for rent/buy properties."""
        return Task(
            config=self.tasks_config["conduct_inspection_calls"],  # type: ignore[index]
        )

    @task
    def conduct_negotiation_calls(self) -> Task:
        """Task for Negotiator to conduct calls for acquisition properties."""
        return Task(
            config=self.tasks_config["conduct_negotiation_calls"],  # type: ignore[index]
        )

    @task
    def compile_call_report(self) -> Task:
        """Task to compile all call results into JSON report."""
        return Task(
            config=self.tasks_config["compile_call_report"],  # type: ignore[index]
            output_file="output/call_results.json",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Call Agent Crew with hierarchical process."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm=llm,
            memory=True,
            planning=True,  # Enable planning for call strategy
            verbose=True,
        )
