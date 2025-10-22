# Train Process Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant TibcoToSpring
    participant LLM
    participant Crew

    User->>Main: TIBCO_DIRECTORY=<tibco_project_directory> crewai train -n <number_of_iterations>
    Main->>TibcoToSpring: TibcoToSpring().crew(training_mode=True)
    TibcoToSpring->>LLM: Initialize LLM with model and cache
    LLM-->>TibcoToSpring: LLM instance
    TibcoToSpring->>Crew: Create crew without external memory
    Crew->>TibcoToSpring: Training process
    TibcoToSpring->>User: Request feedback
    User-->>TibcoToSpring: Provide feedback
    TibcoToSpring->>Output: Save training_data.pkl and trained_agents_data.pkl
    Output-->>TibcoToSpring: Files saved successfully
    TibcoToSpring-->>Main: Training completed
    Main-->>User: Training completed successfully
