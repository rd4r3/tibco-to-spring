# crew.py

from crewai import Crew, Agent, Task, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type,Any
from crewai_tools import FileReadTool, DirectoryReadTool
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

class CompanyCodeInput(BaseModel):
    query: str = Field(..., description="Search query for company code examples")

class CompanyCodeTool(BaseTool):
    name: str = "CompanyCodeExamples"
    description: str = "Search company codebase for implementation examples and patterns"
    args_schema: Type[BaseModel] = CompanyCodeInput

    context_provider: Any

    def _run(self, query: str) -> str:
        return self.context_provider.get_examples(query)

# ------------------ Code Scanner ------------------

def scan_code(path):
    file_types = ["**/*.java", "**/*.xml", "**/*.yml", "**/*.md"]
    loaders = [
        DirectoryLoader(path, glob=pattern, show_progress=True, loader_kwargs={"autodetect_encoding": True})
        for pattern in file_types
    ]

    documents = []
    for loader in loaders:
        documents.extend(loader.load())

    java_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JAVA, chunk_size=1000, chunk_overlap=200
    )
    generic_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

    split_docs = []
    for doc in documents:
        file_path = doc.metadata.get("file_path", "")
        splitter = java_splitter if file_path.endswith(".java") else generic_splitter
        split_docs.extend(splitter.split_documents([doc]))

    return split_docs

# ------------------ Context Provider ------------------

class CompanyCodeContext:
    def __init__(self, base_path):
        self.docs = scan_code(base_path)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index, self.doc_texts = self._build_faiss_index()

    def _build_faiss_index(self):
        texts = [doc.page_content for doc in self.docs]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index, texts

    def get_examples(self, topic, k=3):
        query_map = {
            "controller": (
                "Spring Boot RestController @GetMapping @PostMapping @RequestMapping "
                "HTTP endpoint input validation response entity"
            ),
            "service": (
                "@Service business logic orchestration transactional method delegation "
                "domain service pattern internal API"
            ),
            "repository": (
                "@Repository JPA interface JpaRepository CrudRepository database access "
                "query methods native SQL annotations"
            ),
            "configuration": (
                "@Configuration @Bean application setup dependency injection custom config "
                "property binding environment profiles"
            ),
            "security": (
                "SecurityFilterChain authentication authorization HttpSecurity role-based access "
                "JWT OAuth2 login logout"
            ),
            "exception": (
                "@ControllerAdvice @ExceptionHandler global error handling custom exceptions "
                "response status error mapping"
            ),
            "conversion": (
                "DTO to entity mapping model transformation controller-service-exception flow "
                "MapStruct custom converter"
            ),
            "tibco": (
                "TIBCO BW XML process flow mapping integration orchestration legacy system "
                "adapter transformation activity"
            )
        }

        query = query_map.get(topic, topic)
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, k)
        return "\n\n".join(self.doc_texts[i] for i in indices[0])

    def get_context(self):
        categories = [
            "controller",
            "service",
            "repository",
            "configuration",
            "security",
            "exception",
            "conversion"
        ]
        context_blocks = []
        for category in categories:
            examples = self.get_examples(category)
            context_blocks.append(f"🔹 {category.capitalize()} Examples:\n{examples}")
        return "\n\n".join(context_blocks)

# ------------------ Tool Wrapper ------------------

def setup_company_knowledge_tool(base_path):
    context_provider = CompanyCodeContext(base_path)
    tool = CompanyCodeTool(context_provider=context_provider)
    return tool, context_provider

# ------------------ Agents ------------------


llm_cache = {}
llm = LLM(
    # model="mistral/mistral-large-2411",
    # model="mistral/mistral-large-latest",
    model="mistral/codestral-2508",
    temperature=0.7,
    cache=llm_cache  # Enable caching
)

def create_java_architect(tool):
    return Agent(
        role="Java Architect who enforces company standards",
        goal="""Ensure all generated Spring Boot code strictly follows company architecture, 
        annotations, and logging standards
        """,
        backstory="""
        You are the guardian of company engineering standards. You’ve been trained on thousands of internal code examples and know exactly how controllers, services, repositories, configs, and security modules are structured. You reject anything that deviates from the company’s patterns. You enforce package structure, logging format, exception handling, and API versioning with precision.
        """,
        tools=[tool],
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

def create_tibco_parser(dir_tool, file_tool):
    return Agent(
        role="TIBCO BusinessWorks and BusinessEvents Project Analyst",
        goal="""
        Analyze the architecture and flow of the provided TIBCO BusinessWorks and BusinessEvents project. 
        Identify all components, services, channels, and rule definitions. Examine the core business logic, 
        event-driven interactions, and integration points. Deliver a structured breakdown of each element 
        to provide a clear and complete understanding of the system's behavior and design.
        """,
        backstory="""
        Specialist in dissecting and interpreting TIBCO BusinessWorks and BusinessEvents solutions. 
        Experienced in uncovering hidden dependencies, logic flows, and architectural patterns. 
        Known for delivering precise, actionable insights that support modernization, migration, and optimization efforts.
        You extract flow definitions, service invocations, mappings, and transformation logic from process definitions and prepare them for conversion to Spring Boot.
        """,
        tools=[dir_tool, file_tool],
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

# ------------------ Tasks ------------------

def create_tibco_parsing_task(agent):
    return Task(
        description=f"""
        Perform a comprehensive analysis of the provided TIBCO BusinessEvents and TIBCO BusinessWorks projects, focusing on key architectural 
        and functional components including: business logic, integration points, process definitions, processes and subprocesses, adapters, 
        error handling mechanisms, logging strategies, exception handling, database connection configurations, global variables, event 
        processing flows, preprocessors, decision tables, and rule functions. Deliver a structured breakdown of each element, explaining its 
        role, behavior, and interdependencies. Provide actionable insights on how these components can be mapped, adapted, or re-engineered 
        during migration to Spring Boot. Highlight considerations for preserving functional parity and mitigating migration risks.
        Output a structured summary of the process logic that can be used for Spring Boot conversion.
        """,
        agent=agent,
        expected_output="""
        A detailed technical analysis documenting all relevant aspects of the TIBCO project's architecture and functionality. 
        The output should include clear descriptions of business logic, integration points, process definitions, subprocesses, adapters, 
        error and exception handling mechanisms, logging practices, database configurations, global variables, event processing, 
        preprocessors, decision tables, and rule functions. Structure the analysis to serve as a migration blueprint for developing 
        a Java Spring Boot application that replicates the original TIBCO system with high fidelity. Ensure the documentation is 
        technically precise, migration-aware, and suitable for direct implementation reference.
        """
    )

def create_conversion_task(agent, context_provider):
    return Task(
        description=f"""Convert TIBCO BusinessWorks process to Spring Boot.

        You must strictly follow COMPANY CODE PATTERNS — no deviations, no substitutions. These patterns are extracted directly from production repositories and represent the company's enforced standards.

        {context_provider.get_context()}

        ### Requirements:
        - Package Structure: Use the layer-based structure from company services. Controllers go in .controller, services in .service, repositories in .repository, configs in .config. Do not invent new layers or naming conventions.
        - Exception Handling: Implement a global exception handler using @ControllerAdvice and @ExceptionHandler. Follow the exact structure and response format shown in company examples.
        - Logging Format: Use structured logging with placeholders, e.g. log.info("User created: {{}}", userId). Avoid System.out.println, printStackTrace, or any unstructured logging.
        - API Versioning: Accept version headers using @RequestHeader("API-Version"). Do not use URI-based versioning or query parameters.
        - Controllers: Annotate with @RestController, use @GetMapping, @PostMapping, and follow naming and response patterns from company code.
        - Services: Annotate with @Service, encapsulate business logic, and follow transaction boundaries and method naming conventions.
        - Repositories: Use @Repository and Spring Data JPA. Match entity structure, query methods, and naming from company repositories.
        - Configuration: Use @Configuration and @Bean to define reusable components. Follow company config patterns for metrics, messaging, and security.
        - Security: Implement SecurityFilterChain, authentication filters, and access rules exactly as shown in company security modules. Do not use default Spring Boot security.
        - Use Lombok to reduce boilerplate code.
        - Follow a layered architecture aligned with SOLID principles.
        - Include inline comments (`// TODO`) for future enhancements or clarifications.
        - Ensure strict compliance with the original TIBCO specifications and logic.

        ### Provide a Bash script that automates project setup and compilation, including:
        1. Directory Structure: Commands to create a clean and modular project layout.
        2. Maven `pom.xml`:
            - Include all required libraries.
        3. Java Codebase:
            - REST controllers, service classes, repositories, DTOs/entities, and business logic layers.
            - Unit tests for all core components.
        4. Configuration Files:
            - A default `application.properties` file with essential Spring Boot configurations.
        5. Build Commands:
            - Maven commands to compile and run the application.

        ### Bash Script Requirements:
        - Use proper Bash syntax and handle multiline strings with `cat << 'EOF'`.
        - Ensure the generated project compiles and runs without errors.
        - Include logging to provide runtime visibility.
        - Generate unit test placeholders or implementations for key logic.

        ### Guidelines for Implementation:
        - Maintain clean, modular, and well-documented code.
        - Validate that the Bash script produces a fully functional Spring Boot application.
        - Ensure the final application mirrors the original TIBCO workflows and logic with precision.
        """,
        agent=agent,
        expected_output=f"""
        A complete Spring Boot application matching company standards, that replicates the full functionality of the original TIBCO BusinessWorks and BusinessEvents projects. 
        The application should preserve business logic, workflows, and integration behavior. Deliverables must follow best practices in Spring Boot 
        development, including modular architecture, clean code, and proper dependency management.
        """
    )

# ------------------ Crew Setup ------------------

def create_crew(base_path="./company-repos", tibco_path="./tibco-project"):
    tool, context_provider = setup_company_knowledge_tool(base_path)
    java_architect = create_java_architect(tool)
    tibco_parser = create_tibco_parser(DirectoryReadTool(directory=tibco_path), FileReadTool())

    task_parse = create_tibco_parsing_task(tibco_parser)
    task_convert = create_conversion_task(java_architect, context_provider)

    return Crew(
        agents=[tibco_parser, java_architect],
        tasks=[task_parse, task_convert],
        verbose=True
    )
