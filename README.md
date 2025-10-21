# 🧠 Tibco to Spring

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Powered%20by%20CrewAI-blue)](https://crewai.com)
[![MistralAI](https://img.shields.io/badge/MistralAI-Powered%20by%20MistralAI-blue)](https://mistral.ai/)

Welcome to the **TibcoToSpring** — a multi-agent AI system powered by [CrewAI](https://crewai.com), designed to convert legacy TIBCO workflows into modern Spring Boot applications.

## 🚀 Features

- Analyzes your TIBCO project
- Generates bash scripts to scaffold Spring Boot projects

## 🛠️ Installation

### 1. Prerequisites

- Python **≥ 3.10 and ≤ 3.13**
- [UV](https://docs.astral.sh/uv/) for dependency management

### 2. Install UV

```bash
pip install uv
```

### 3. Clone the Repository

```bash
git clone https://github.com/rd4r3/tibco-to-spring.git
cd tibco-to-spring
```

### 4. Install CrewAI

```bash
uv tool install crewai
```

### 5. Install Dependencies

```bash
crewai install
```

### 6. Set Up Environment Variables

Create a `.env` file in the root directory and add your Mistral API key:

```env
MISTRAL_API_KEY=your_key_here
```

## ▶️ Running the Project

From the root folder, launch your crew:

```bash
TIBCO_DIRECTORY=<tibco_project_directory> crewai run
```

This will initialize the agents and execute tasks. The output includes a `bash_script` in the `outputs/` folder, which can be used to generate a complete Spring Boot project.

## 🧑‍🤝‍🧑 Understanding Your Crew

Each agent is defined in `agents.yaml` with specific goals and tools. Tasks are orchestrated via `tasks.yaml`, enabling collaborative execution across agents.

## 📚 Support & Resources

- [CrewAI Documentation](https://docs.crewai.com)
