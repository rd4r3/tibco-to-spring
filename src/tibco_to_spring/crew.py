from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.memory.long_term.long_term_memory import LongTermMemory, LTMSQLiteStorage
from crewai_tools import FileReadTool
from pathlib import Path
from pydantic import BaseModel, Field, validator
import os
# Uncomment the following line to use an example of a custom tool
# from tibco_to_spring.tools.custom_tool import MyCustomTool
# Uncomment the following line to use an example of a knowledge source
# from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool



# class MistralEmbedder:
#     def __init__(self, model_name: str, api_key: str):
#         self.model_name = model_name
#         self.api_key = api_key
#         self.api_url = "https://api.mistral.ai/v1/embeddings"

#     def embed(self, input_text: str):
#         import requests
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "model": self.model_name,
#             "input": text
#         }
#         response = requests.post(self.api_url, headers=headers, json=payload)
#         response.raise_for_status()
#         return response.json()["data"][0]["embedding"]


class JavaSpringBoot(BaseModel):
    bash: str = Field(description="bash script to generate Java Spring Boot project")
    # feedback: str = Field(description="feedback JSON with status and message")

    @validator('bash')
    def format_bash_script(cls, v: str) -> str:
        """Ensure bash script is properly formatted"""
        # Handle JSON string input
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict) and 'bash' in parsed:
                    v = parsed['bash']
            except json.JSONDecodeError:
                # Not JSON, treat as raw bash script
                pass

        # Normalize line endings
        v = v.replace('\r\n', '\n')
        
        # Add shebang if missing
        if not v.startswith('#!/bin/bash'):
            v = '#!/bin/bash\n' + v
        
        lines = []
        in_heredoc = False
        heredoc_marker = None
        
        # Split while preserving empty lines
        script_lines = v.splitlines(keepends=True)
        
        for line in script_lines:
            # Handle heredoc start
            if 'cat << ' in line:
                in_heredoc = True
                heredoc_marker = line.split('cat << ')[-1].strip("'\"")
                lines.append(line.rstrip())
                continue
            
            # Handle heredoc content
            if in_heredoc:
                if line.strip() == heredoc_marker:
                    in_heredoc = False
                    lines.append(line.rstrip())
                else:
                    # Preserve exact formatting inside heredoc
                    lines.append(line)
                continue
            
            # Handle normal bash commands
            if line.strip():
                if any(line.strip().startswith(cmd) for cmd in ('mkdir', 'cd', 'mvn', 'echo')):
                    lines.append(line.strip())
                else:
                    # Preserve formatting for other commands
                    lines.append(line.rstrip())
            else:
                # Skip empty lines
                continue
        
        # Remove extra whitespace
        script = '\n'.join(lines)
        script = re.sub(r'\n\s*\n', '\n', script)  # Remove consecutive empty lines
        script = re.sub(r'>\s+pom.xml', '> pom.xml', script) # Remove spaces after > pom.xml
        return script

@CrewBase
class TibcoToSpring():
	"""TibcoToSpring crew"""

	DB_ROOT_PATH = "src\\tibco_to_spring\\.db"
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	llm = LLM(
		model="mistral/mistral-large-latest",
		temperature=0.7
	)
	long_term_memory = LongTermMemory(
		storage=LTMSQLiteStorage(db_path=f"{DB_ROOT_PATH}\\tibco_to_spring.db")
    )
	file_read_tool = FileReadTool(
		file_path=Path('src\\tibco_to_spring\\data\\tibco_credit_maintanence_project.txt'),
		description='A tool to read the tibco project file.'
	)
	# embedder = MistralEmbedder(
	# 	model_name="mistral-embed-light",
	# 	api_key=os.environ.get("MISTRAL_API_KEY")
	# )
	embedder={
		"provider": "mistral", # Match your LLM provider
		"config": {
			"api_key": os.environ.get("MISTRAL_API_KEY"),
			"model": "mistral-embed-light"
		}
    }

	# @before_kickoff # Optional hook to be executed before the crew starts
	# def pull_data_example(self, inputs):
	# 	# Example of pulling data from an external API, dynamically changing the inputs
	# 	inputs['extra_data'] = "This is extra data"
	# 	return inputs

	# @after_kickoff # Optional hook to be executed after the crew has finished
	# def log_results(self, output):
	# 	# Example of logging results, dynamically changing the output
	# 	print(f"Results: {output}")
	# 	return output

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
            context=[self.tibco_analyze_task()],            
            output_json=JavaSpringBoot
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the TibcoToSpring crew"""
		# You can add knowledge sources here
		# knowledge_path = "user_preference.txt"
		# sources = [
		# 	TextFileKnowledgeSource(
		# 		file_path="knowledge/user_preference.txt",
		# 		metadata={"preference": "personal"}
		# 	),
		# ]

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
            # memory=True,
			# embedder=self.embedder,
            # long_term_memory=self.long_term_memory
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
			# knowledge_sources=sources, # In the case you want to add knowledge sources
		)
