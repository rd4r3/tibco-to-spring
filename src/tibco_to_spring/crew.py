from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool
import json
import os
import re
from tibco_to_spring.local_vector_memory import LocalVectorMemory
from crewai.memory.external.external_memory import ExternalMemory

@CrewBase
class TibcoToSpring():
	"""TibcoToSpring crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	dir_tool = DirectoryReadTool(directory='tibco_samples/CreditMaintenance')
	file_tool = FileReadTool()
	memory = ExternalMemory(storage=LocalVectorMemory())
	llm_cache = {}
	llm = LLM(
        model="mistral/mistral-large-2411",
        # model="mistral/mistral-large-latest",
        temperature=0.7,
        cache=llm_cache  # Enable caching
    )

	@agent
	def tibco_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['tibco_analyst'],
			tools=[self.dir_tool, self.file_tool],
			llm=self.llm,
			verbose=True,
			allow_delegation=False
		)

	@agent
	def java_architect(self) -> Agent:
		return Agent(
			config=self.agents_config['java_architect'],
			verbose=True,
			llm=self.llm,
			allow_delegation=False
		)

	@task
	def analyze_tibco(self) -> Task:
		return Task(
			config=self.tasks_config['analyze_tibco'],
			agent=self.tibco_analyst()
		)

	@task
	def create_spring_boot(self) -> Task:
		return Task(
			config=self.tasks_config['create_spring_boot'],
			agent=self.java_architect(),
			context=[self.analyze_tibco()]
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the TibcoToSpring crew"""
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
			external_memory=self.memory,
			timeout=1000
		)
