# Run Process Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant TibcoToSpring
    participant LLM
    participant Crew
    participant Output

    User->>Main: TIBCO_DIRECTORY=<tibco_project_directory> crewai run
    Main->>TibcoToSpring: TibcoToSpring().crew().kickoff()
    TibcoToSpring->>LLM: Initialize LLM with model and cache
    LLM-->>TibcoToSpring: LLM instance
    TibcoToSpring->>Crew: Create crew with agents and tasks
    Crew->>TibcoToSpring: crew_output
    TibcoToSpring-->>Main: crew_output
    Main->>Output: Write bash script to file
    Output-->>Main: File created successfully
    Main-->>User: Files created successfully
