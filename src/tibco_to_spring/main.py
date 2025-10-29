#!/usr/bin/env python
import os
import sys
import warnings
from pathlib import Path
from tibco_to_spring.crew import TibcoToSpring
from tibco_to_spring.logging_config import get_logger
from tibco_to_spring.compact.crew import create_crew

# Constants
OUTPUT_DIR = Path("outputs")
BASH_FILE = OUTPUT_DIR / "bash_script.sh"

# Set up logging
logger = get_logger(__name__)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# def run() -> None:
#     try:
#         # Get crew output
#         crew_output = TibcoToSpring().crew().kickoff()

#         # Ensure output directories exist
#         OUTPUT_DIR.mkdir(exist_ok=True)

#         # Write bash script to the springBootProject directory
#         BASH_FILE.write_text(crew_output.raw, encoding="utf-8")
#         if os.name != "nt":  # Not Windows
#             BASH_FILE.chmod(BASH_FILE.stat().st_mode | 0o755)

#         logger.info(f"Files created successfully in {OUTPUT_DIR.absolute()}")

#     except Exception as e:
#         raise IOError(f"Error processing output: {e}")

def train() -> None:
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "Tibco To Spring Boot"
    }
    try:
        TibcoToSpring().crew(training_mode=True).train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
        logger.info("Training completed successfully")

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

# COMPACT VERSION WITH CODE INSPECTION
def run() -> None:
    try:
        # Get crew output
        crew = create_crew(
            base_path="<>",
            tibco_path="<>"
        )
        crew_output = crew.kickoff()

        # Ensure output directories exist
        OUTPUT_DIR.mkdir(exist_ok=True)

        # Write bash script to the springBootProject directory
        BASH_FILE.write_text(crew_output.raw, encoding="utf-8")
        if os.name != "nt":  # Not Windows
            BASH_FILE.chmod(BASH_FILE.stat().st_mode | 0o755)

        logger.info(f"Files created successfully in {OUTPUT_DIR.absolute()}")

    except Exception as e:
        raise IOError(f"Error processing output: {e}")