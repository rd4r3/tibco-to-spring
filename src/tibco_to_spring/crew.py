from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool
import json
import os
import re
import time
from functools import wraps
from tibco_to_spring.local_vector_memory import LocalVectorMemory
from crewai.memory.external.external_memory import ExternalMemory


@CrewBase
class TibcoToSpring():
	"""TibcoToSpring crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	# Simple cache for LLM responses
	llm_cache = {}

	# Rate limiting decorator
	def rate_limit(max_per_minute: int):
		"""Decorator to limit function calls to max_per_minute"""
		min_interval = 60.0 / float(max_per_minute)

		def decorator(func):
			last_called = [0.0]

			@wraps(func)
			def wrapper(*args, **kwargs):
				elapsed = time.time() - last_called[0]
				wait_time = min_interval - elapsed
				if wait_time > 0:
					time.sleep(wait_time)
				last_called[0] = time.time()
				return func(*args, **kwargs)
			return wrapper
		return decorator

	# Apply rate limiting to LLM calls
	@rate_limit(max_per_minute=30)  # Adjust based on your API limits
	def rate_limited_llm_call(llm_instance, *args, **kwargs):
		return llm_instance(*args, **kwargs)

	llm = LLM(
		# model="mistral/codestral-2501",
		model="mistral/mistral-large-latest",
		temperature=0.7,
		cache=llm_cache  # Enable caching
	)
	dir_tool = DirectoryReadTool(directory='src/tibco_to_spring/data')
	file_tool = FileReadTool()
	memory = ExternalMemory(storage=LocalVectorMemory())

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
