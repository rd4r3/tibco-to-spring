from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool
import os
from tibco_to_spring.local_vector_memory import LocalVectorMemory
from crewai.memory.external.external_memory import ExternalMemory

@CrewBase
class TibcoToSpring():
	"""TibcoToSpring crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	tibco_directory = os.getenv('TIBCO_DIRECTORY', 'tibco_samples/FintechTransactionProcessorAsString')
	print(f"Using TIBCO directory: {tibco_directory}")
	dir_tool = DirectoryReadTool(directory=tibco_directory)
	file_tool = FileReadTool()

	# Create a unique memory instance for each crew run
	def _create_memory(self):
		return ExternalMemory(storage=LocalVectorMemory())

	llm_cache = {}
	llm = LLM(
        # model="mistral/mistral-large-2411",
        # model="mistral/mistral-large-latest",
		model="mistral/codestral-2508",
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

	@agent
	def java_reviewer(self) -> Agent:
		return Agent(
			config=self.agents_config['java_reviewer'],
			verbose=True,
			llm=self.llm,
			allow_delegation=False
		)

	@task
	def analyze_tibco(self) -> Task:
		return Task(
			config=self.tasks_config['analyze_tibco']
		)

	@task
	def create_spring_boot(self) -> Task:
		return Task(
			config=self.tasks_config['create_spring_boot'],
			context=[self.analyze_tibco()]
		)

	@task
	def review_spring_boot(self) -> Task:
		return Task(
			config=self.tasks_config['review_spring_boot'],
			context=[self.create_spring_boot()]
		)

	@crew
	def crew(self, training_mode: bool = False) -> Crew:
		"""Creates the TibcoToSpring crew

		Args:
			training_mode: If True, excludes external_memory from the crew initialization
		"""
		crew_kwargs = {
			'agents':self.agents,
			'tasks':self.tasks,
			'process': Process.sequential,
			'verbose': True,
			'timeout': 1000
		}

		# Only include external_memory if not in training mode
		if not training_mode:
			crew_kwargs['external_memory'] = self._create_memory()

		return Crew(**crew_kwargs)
