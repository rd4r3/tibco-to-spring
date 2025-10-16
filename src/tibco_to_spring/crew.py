from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool
from pathlib import Path
from pydantic import BaseModel, Field, validator
import json
import os
import re
import time
from functools import wraps
from tibco_to_spring.tools.custom_tool import MyCustomTool
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai_tools import SerperDevTool
from tibco_to_spring.local_vector_memory import LocalVectorMemory
from crewai.memory.external.external_memory import ExternalMemory


@CrewBase
class TibcoToSpring():
	"""TibcoToSpring crew"""

	DB_ROOT_PATH = "src/tibco_to_spring/.db"
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
		model="mistral/codestral-2501",
		# model="mistral/mistral-medium-latest",
		temperature=0.7,
		cache=llm_cache  # Enable caching
	)
	file_read_tool = FileReadTool(
		file_path=Path('src/tibco_to_spring/data/tibco_credit_maintanence_project.txt'),
		description='A tool to read the tibco project file.'
	)

	memory = ExternalMemory(storage=LocalVectorMemory())

	@agent
	def tibco_analyze_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['tibco_analyze_agent'],
			tools=[self.file_read_tool],
			llm=self.llm,
			verbose=True,
			allow_delegation=False
		)

	@agent
	def java_architect_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['java_architect_agent'],
			verbose=True,
			llm=self.llm,
			allow_delegation=False
		)

	@task
	def tibco_analyze_task(self) -> Task:
		return Task(
			config=self.tasks_config['tibco_analyze_task'],
			tools=[self.file_read_tool],
			agent=self.tibco_analyze_agent()
		)

	@task
	def create_spring_boot_task(self) -> Task:
		return Task(
			config=self.tasks_config['create_spring_boot_task'],
			agent=self.java_architect_agent(),
			context=[self.tibco_analyze_task()]
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
