#!/usr/bin/env python
import sys
import warnings
from pathlib import Path
import os, json
from tibco_to_spring.crew import TibcoToSpring, JavaSpringBoot

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    try:
        # Get crew output
        crew_output = TibcoToSpring().crew().kickoff()
        #crew_output = get_dummy_output()  # For testing

        print("<<<<<<<<<<<<<<<<<<<Result from custom kickoff: ", crew_output)

        # Handle different output formats
        if isinstance(crew_output, str):
            try:
                crew_output = json.loads(crew_output)
            except json.JSONDecodeError:
                crew_output = {"bash": crew_output}

        # Create model instance with properly formatted input
        java_spring_boot = JavaSpringBoot(bash=crew_output["bash"])

        # Create output directory
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        # Create springBootProject directory inside outputs
        spring_boot_dir = output_dir / "springBootProject"
        spring_boot_dir.mkdir(exist_ok=True)

        # Write bash script to the springBootProject directory
        bash_file = spring_boot_dir / "bash_script.sh"
        bash_file.write_text(java_spring_boot.bash, encoding="utf-8")
        if os.name != "nt":  # Not Windows
            bash_file.chmod(bash_file.stat().st_mode | 0o755)

        # # Write feedback JSON
        # feedback_file = output_dir / "feedback.json"
        # feedback_file.write_text(java_spring_boot.feedback, encoding='utf-8')

        print(f"Files created successfully in {output_dir.absolute()}")

        return True

    except KeyError as e:
        raise ValueError(f"Missing required field in crew output: {e}")
    except Exception as e:
        raise IOError(f"Error processing output: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        TibcoToSpring().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TibcoToSpring().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        TibcoToSpring().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
