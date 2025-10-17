#!/usr/bin/env python
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, Any, Union
from tibco_to_spring.crew import TibcoToSpring

# Constants
OUTPUT_DIR = Path("outputs")
BASH_FILE = OUTPUT_DIR / "bash_script.sh"
# FEEDBACK_FILE = OUTPUT_DIR / "feedback.json"

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run() -> None:
    try:
        # Get crew output
        crew_output = TibcoToSpring().crew().kickoff()

         # Ensure output directories exist
        OUTPUT_DIR.mkdir(exist_ok=True)

        # Write bash script to the springBootProject directory
        BASH_FILE.write_text(crew_output.raw, encoding="utf-8")
        if os.name != "nt":  # Not Windows
            BASH_FILE.chmod(BASH_FILE.stat().st_mode | 0o755)

        print(f"Files created successfully in {OUTPUT_DIR.absolute()}")

    except KeyError as e:
        raise ValueError(f"Missing required field in crew output: {e}")
    except Exception as e:
        raise IOError(f"Error processing output: {e}")
